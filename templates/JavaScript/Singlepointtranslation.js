/**
 * Created by casm on 2018/4/26.
 */
var Singlepointtranslation =function(){
    function selectlanguages() {
        var selectval = $("#selectlanguages").val();
        if (selectval == "英语") {
            //条件
        }else if(selectval == "法语"){
            //条件
        }else if(selectval == "德语"){
            //条件
        }else if(selectval == "阿拉伯语"){
            //条件
        }else if(selectval == "西班牙语"){
            //条件
        }


    }

    //点击翻译
    $('#button').click(function () {
        var input = $('#inputvalue').val().trim();
        $.ajax({
            type: "post",
            url: "http://localhost:5555/translation?source="+input, //Controller中的方法名
            data: { "input":input },     //要发送的数据
            dataType: "json",
            success: function(data) {
                //$('#outputvalue').val(data);
                $('#outputvalue').val(data.transContext);
                //$('#explain').val(data.tag);
                //$('#explain').val(data.log);
                var m=data.tag;
                var n=m.toString();
                console.log(n);
                var k= n.replace(-1,"未翻译").replace(0,"音译").replace(1,"特殊字符").replace(2,"意译");

                $('#explainvalue').val(k+"\n"+data.log);
            },
            error: function(err) {
                alert("请重新输入");
            }

            });
    });



}