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
        'uploadScript': "http://localhost:5555/upload",
        'queueID': 'uploadProgress1',//文件列队
        'queueSizeLimit': 100,//上传的最大数量
        //'fileType': 'application/msword',
        'multi': true,
        'buttonText': '文件上传',//按钮显示文字
        'onUpload': function (file) {
            // 隐藏信息提示框，显示上传文件队列
            $('#uploadTips1').css('display', 'none');
            $('#uploadProgress1').css('display', 'block');
        },
        'onUploadComplete': function (file, data) {
            if (data) {
                alert('上传成功')
            } else {
                alert('上传失败' + rspdesc);
            }
        }
    })

}