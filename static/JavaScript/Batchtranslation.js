/**
 * Created by casm on 2018/4/26.
 */
//批量翻译
var Batchtranslation = function () {
    //上传文件
    $('#filePicker').uploadifive({

        'auto': true,//自动提交
        'height': 100,
        'method': 'POST',
        //'uploadScript': "publishInfo/parseUploadData.action?filetype=file&pubtype=" + $('#file-pubtype').val() + "&rand=" + Math.random(),
        'uploadScript': "/upload",
        //'uploadScript': '/File/UploadFile',
        'queueID': 'uploadProgress1',//文件列队
        'queueSizeLimit': 100,//上传的最大数量
        "fileType": "txt/*",
        'multi': true,
        "formData":{'enctype' : 'multipart/form-data'},
        'buttonText': '文件上传',//按钮显示文字
        'onUpload': function (file) {
            // 隐藏信息提示框，显示上传文件队列
            $('#uploadTips1').css('display', 'none');
            $('#uploadProgress1').css('display', 'block');
        },
        'onUploadComplete': function (file) {
                alert('上传成功')
        }
    });
    //保存
    $('#btnPubSave1').click(function() {
        // 清空上传队列
        $('#filePicker').uploadifive('clearQueue');
        // 显示信息提示框，隐藏上传文件队列
        $('#uploadTips1').css('display', 'block');
        $('#uploadProgress1').css('display', 'none');
    });
    //取消
    $('#btnPubCancel1').click(function(){
        $('#shpPicker').uploadifive('clearQueue');
        // 显示信息提示框，隐藏上传文件队列
        $('#uploadTips1').css('display','block');
        $('#uploadProgress1').css('display','none');
    })

}