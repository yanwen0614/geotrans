mosesdecoder/scripts/recaser/train-truecaser.perl --model corpus/truecase-model.phonetic --corpus corpus/phonetic
mosesdecoder/scripts/recaser/train-truecaser.perl --model corpus/truecase-model.word --corpus corpus/word


mosesdecoder/scripts/recaser/truecase.perl    --model corpus/truecase-model.phonetic   < corpus/phonetic   > corpus/truecase.phonetic
mosesdecoder/scripts/recaser/truecase.perl    --model corpus/truecase-model.word   < corpus/word   > corpus/truecase.word
mosesdecoder/scripts/training/clean-corpus-n.perl corpus/truecase phonetic word corpus/clean 1 80

mosesdecoder/scripts/recaser/truecase.perl --model corpus/truecase-model.phonetic   < corpus/phonetictest > corpus/truecase.phonetictest
mosesdecoder/scripts/recaser/truecase.perl --model corpus/truecase-model.word   < corpus/wordtest > corpus/truecase.wordtest

mosesdecoder/bin/lmplz -o 3 < corpus/clean.phonetic > lm/phonetic.w-p.arpa --discount_fallback
mosesdecoder/bin/build_binary  lm/phonetic.w-p.arpa  lm/phonetic.w-p.blm

nohup nice mosesdecoder/scripts/training/train-model.perl -cores 4 -root-dir train  -corpus corpus/clean -f word -e phonetic -alignment grow-diag-final-and -reordering msd-bidirectional-fe  -lm 0:3:/mnt/d/项目/地名翻译/新建文件夹/lm/phonetic.w-p.blm:8  -external-bin-dir mosesdecoder/tools >& training.out &

nohup nice  mosesdecoder/scripts/training/mert-moses.pl -threads 4 corpus/truecase.wordtest corpus/truecase.phonetictest mosesdecoder/bin/moses train/model/moses.ini --mertdir /mnt/d/项目/地名翻译/新建文件夹/mosesdecoder/bin/ &> mert.out &   

mosesdecoder/bin/processPhraseTableMin   -in train/model/phrase-table.gz   -out binarised-model/phrase-table
mosesdecoder/bin/processLexicalTableMin   -in train/model/reordering-table.wbe-msd-bidirectional-fe.gz  -out binarised-model/reordering-table

bash
echo 'l o s a l t o s' | mosesdecoder/bin/moses   -f mert-work/moses.ini  
exit

echo 'l o s a l t o s' | cd

nice mosesdecoder/bin/moses    -f mert-work/moses.ini   
   <                
   > 
   2>  
