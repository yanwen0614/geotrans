from __future__ import print_function


import codecs
import time

import numpy as np
import tensorflow as tf
import argparse


from nmt import train
from nmt.utils import evaluation_utils
from nmt.utils import misc_utils as utils
from nmt.utils import vocab_utils
from nmt import attention_model, gnmt_model
from nmt import model as nmt_model
from nmt import model_helper
from nmt.nmt import create_or_load_hparams
from nmt.utils import nmt_utils



utils.check_tensorflow_version()

FLAGS = None

class nmt_w2p(object):

  infer_model = None

  def __init__(self,jobdirs, target_session=""):
    """Run main."""
    # Job
    jobid = 1
    num_workers = 1
    #utils.print_out("# Job id %d" % jobid)

    out_dir = jobdirs
    if not tf.gfile.Exists(out_dir):
      raise FileNotFoundError

    # Load hparams.
    hparams = utils.load_hparams(jobdirs)
    self.hparams = hparams
    # Inference
    ckpt = tf.train.latest_checkpoint(out_dir)
    self.ckpt = ckpt
    #print("inference_fn_para",ckpt, hparams, num_workers, jobid)
    self.inference(ckpt,hparams, num_workers, jobid)

  def inference(self,ckpt,hparams,num_workers=1,jobid=0,scope=None):
    """Perform translation."""
    if not hparams.attention:
      #print("not hparams.attention")
      model_creator = nmt_model.Model
    elif hparams.attention_architecture == "standard":
      #print("attention_standard")
      model_creator = attention_model.AttentionModel
    elif hparams.attention_architecture in ["gnmt", "gnmt_v2"]:
      #print("gnmt")
      model_creator = gnmt_model.GNMTModel
    else:
      raise ValueError("Unknown model architecture")
    self.infer_model = model_helper.create_infer_model(model_creator, hparams, scope)
    """
    print("create_infer_model")
    self.sess = tf.Session(graph=self.infer_model.graph, config=utils.get_config_proto())
    self.loaded_infer_model = model_helper.load_model(self.infer_model.model, ckpt, self.sess, "infer")
    """

  def translation(self,infer_data,):
    """translation Inference with a single worker."""
    infer_model = self.infer_model
    # Read data
    if not isinstance(infer_data,list):
      infer_data = [infer_data]
    #print("infer_data",infer_data)
    start_time = time.time()

    with tf.Session(graph=infer_model.graph, config=utils.get_config_proto()) as sess:
      loaded_infer_model = model_helper.load_model(infer_model.model, self.ckpt, sess, "infer")

      #print("load model",start_time - time.time())
      sess.run(
          self.infer_model.iterator.initializer,
          feed_dict={
              self.infer_model.src_placeholder: infer_data,
              self.infer_model.batch_size_placeholder: self.hparams.infer_batch_size}
              )
      # Decode
      #utils.print_out("# Start decoding")
      res = self.decode(
          loaded_infer_model,
          sess,
          beam_width=0,
          tgt_eos="</s>",
          num_translations_per_input=1)
      #print("total model",start_time - time.time())
      return res
    """
    sess =  tf.Session(graph=infer_model.graph, config=utils.get_config_proto())
    infer_model.model.saver.restore(sess, self.ckpt)
    a = tf.tables_initializer()
    sess.run(a)

    print("load model",start_time - time.time())
    sess.run(
        infer_model.iterator.initializer,
        feed_dict={
            infer_model.src_placeholder: infer_data,
            infer_model.batch_size_placeholder: self.hparams.infer_batch_size}
            )
    # Decode
    #utils.print_out("# Start decoding")
    res = self.decode(
        infer_model,
        sess,
        beam_width=0,
        tgt_eos="</s>",
        num_translations_per_input=1)
    return res
    """
  def decode(self,model,sess,beam_width,tgt_eos,num_translations_per_input=1,):
    """Decode a test set and compute a score according to the evaluation task."""
    # Decode
    #utils.print_out("Start decoding." )
    start_time = time.time()
    num_sentences = 0
    res = []
    num_translations_per_input = max(
      min(num_translations_per_input, beam_width), 1)
    while True:
      try:
        nmt_outputs, _ = model.decode(sess)
        if beam_width == 0:
          nmt_outputs = np.expand_dims(nmt_outputs, 0)
        batch_size = nmt_outputs.shape[1]
        num_sentences += batch_size
        for sent_id in range(batch_size):
          for beam_id in range(num_translations_per_input):
            translation = self.get_translation_text(
                nmt_outputs[beam_id],
                sent_id,
                tgt_eos=tgt_eos,
              )
            res.append(translation.decode("utf-8"))
      except tf.errors.OutOfRangeError:
        #utils.print_time( "  done, num sentences %d, num translations per input %d" %(num_sentences, num_translations_per_input), start_time)
        #print("load model",start_time - time.time())
        break
    return res

  def get_translation_text(self,nmt_outputs, sent_id, tgt_eos, subword_option=""):
    """Given batch decoding outputs, select a sentence and turn to text."""
    if tgt_eos: tgt_eos = tgt_eos.encode("utf-8")
    # Select a sentence
    output = nmt_outputs[sent_id, :].tolist()

    # If there is an eos symbol in outputs, cut them at that point.
    if tgt_eos and tgt_eos in output:
      output = output[:output.index(tgt_eos)]

    if subword_option == "bpe":  # BPE
      translation = utils.format_bpe_text(output)
    elif subword_option == "spm":  # SPM
      translation = utils.format_spm_text(output)
    else:
      translation = utils.format_text(output)

    return translation


def add_arguments(parser):
  """Build ArgumentParser."""
  parser.register("type", "bool", lambda v: v.lower() == "true")

  # network
  parser.add_argument("--mode", type=str, default="batch", help="single | batch ")
  parser.add_argument("--word", type=str, default="", help="word to trans")
  parser.add_argument("--infile", type=str,  help="word to trans")
  parser.add_argument("--outfile", type=str, help="word to trans")

def singleword(jobdirs,word):
  infer_data = [word]
  trans =  nmt_w2p(jobdirs)
  res = trans.translation(infer_data)
  return res

def batch(jobdirs,outfile,infile):
    from utils.Modify import Modify
    Modify = Modify()
    trans =  nmt_w2p(jobdirs)
    f = open(infile,mode="r",encoding="utf8")
    wordlist = []
    wordcount = []
    for l in f:
        a = Modify.modifyphrase(l)
        a = a.rsplit()
        wordlist.extend([" ".join(aa).lower() for aa in a])
        wordcount.append(len(a))
    res = trans.translation(wordlist)
    tag = 0
    ff = open(outfile,mode="w",encoding="utf8")
    for r in res:
        if wordcount[0]==0:
            ff.write("\n")
            wordcount = wordcount[1:]
        wordcount[0]-=1
        ff.write(r)
        if wordcount[0]==0:
            ff.write("\n")
            wordcount = wordcount[1:]
        else:
            ff.write(",")

if __name__ == "__main__":
  nmt_parser = argparse.ArgumentParser()
  add_arguments(nmt_parser)
  FLAGS, unparsed = nmt_parser.parse_known_args()
  print(FLAGS)
  jobdirs = "./model/nmt_model_w2p_2_64_200000_bi_at_nadam"
  if FLAGS.mode == "single":
    word = ' '.join(FLAGS.word.lower())
    res = singleword(jobdirs,word)
    print(*res)
  elif FLAGS.mode == "batch":
    batch(jobdirs,FLAGS.outfile,FLAGS.infile)




