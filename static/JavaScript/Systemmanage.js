/**
 * Created by casm on 2018/6/4.
 */
var Systemmanage = function () {

    //专名库管理
    $('#btnSpecialManage').click(function () {
        //alert("你好");
        $('#sptablepanel').css('display', 'block');
        $('#getablepanel').css('display', 'none');
        $('#ruletablepanel').css('display', 'none');

        $(this).css('background-image', "url('images/menu4/feedback-selected.png')").find("label").css('color', '#007DF0');
        $('#btnGeneralManage').css('background-image', "url('images/menu4/feedback.png')").find("label").css('color', '');
        $('#btnRuleManage').css('background-image', "url('images/menu4/feedback.png')").find("label").css('color', '');
        SpecialmanageTables();
    });
    //通名库管理
    $('#btnGeneralManage').click(function () {
        //alert("哈哈");
        $('#sptablepanel').css('display', 'none');
        $('#getablepanel').css('display', 'block');
        $('#ruletablepanel').css('display', 'none');

        $(this).css('background-image', "url('images/menu4/feedback-selected.png')").find("label").css('color', '#007DF0');
        $('#btnSpecialManage').css('background-image', "url('images/menu4/feedback.png')").find("label").css('color', '');
        $('#btnRuleManage').css('background-image', "url('images/menu4/feedback.png')").find("label").css('color', '');
        GeneralmanageTables();
    });
    //规则库管理
    $('#btnRuleManage').click(function () {
        //alert("哈哈");
        $('#sptablepanel').css('display', 'none');
        $('#getablepanel').css('display', 'none');
        $('#ruletablepanel').css('display', 'block');

        $(this).css('background-image', "url('images/menu4/feedback-selected.png')").find("label").css('color', '#007DF0');
        $('#btnSpecialManage').css('background-image', "url('images/menu4/feedback.png')").find("label").css('color', '');
        $('#btnGeneralManage').css('background-image', "url('images/menu4/feedback.png')").find("label").css('color', '');
        RulemanageTables();
    });
    var SpecialmanageTables = function () {
        $('#sptablepanel').layout('resize');
        $('#dg1').datagrid({
            title: '专名库',
            rownumbers: true,
            singleSelect: false,
            autoRowHeight: false,
            pagination: true,
            pageSize: 40,
            pagePosition: 'bottom',
            fitColumns: true,
            striped: true,
            method: 'POST',
            url: '/getInstance',
            queryParams: {
                start:1,
                end:20
            },
            columns: [[
                {field: 'ck', checkbox: true},
                {field: 'id', title: 'id', hidden: true},
                {field: 'romanname', title: '罗马地名', width: 100, halign: 'center', align: 'center', editor: 'textbox'},
                {field: 'deputy1', title: '副条1', width: 100, halign: 'center', align: 'center', editor: 'textbox'},
                {field: 'deputy2', title: '副条2', width: 100, halign: 'center', align: 'center', editor: 'textbox'},
                {field: 'chinesename', title: '中文地名', width: 100, halign: 'center', align: 'center', editor: 'textbox'},
                {
                    field: 'chinesenamedeputy',
                    title: '中文地名副条',
                    width: 100,
                    halign: 'center',
                    align: 'center',
                    editor: 'textbox'
                },
                {
                    field: 'countries',
                    title: '国家',
                    width: 100,
                    halign: 'center',
                    align: 'center',
                    editor: 'textbox',
                    // fixed: true
                },
                {
                    field: 'long',
                    title: '经度',
                    width: 100,
                    halign: 'center',
                    editor: 'textbox',
                    align: 'center',
                    // fixed: true
                },
                {field: 'lat', title: '纬度', width: 100, halign: 'center', align: 'center', fixed: true},
                //{
                //    field: 'operate', title: '操作', width: 150, align: 'center',
                //    formatter: function (value, row, index) {
                //        return '<a href="#" style="color: #317ee8" onclick="APPVAR.mainMenu.m4.operaUserModify(' + index + ')">修改</a>' +
                //            '<a style="margin:0 5px; border-right: 1px solid #317ee8;"></a>' +
                //            '<a href="#" style="color: #ff4c4c" onclick="APPVAR.mainMenu.m4.operaUserDelete(' + index + ')">删除</a>'
                //    }
                //}
            ]],
            // toolbar: '#spTableToolbar',
            onBeforeLoad: function () {
                var $title = $('.panel-title');
                $title.html('<a style="margin:0 8px;border-right: 3px solid #317ee8;"></a>专名库');
            }
        });
    };

    var GeneralmanageTables = function () {
        $('#getablepanel').layout('resize');
        $('#dg2').datagrid({
            title: '通名库',
            rownumbers: true,
            singleSelect: false,
            autoRowHeight: false,
            pagination: true,
            pageSize: 20,
            pagePosition: 'bottom',
            fitColumns: true,
            striped: true,
            method: 'POST',
            url: '/getGenricInstance',
            queryParams: {
                start:1,
                end:100
            },

            columns: [[
                {field: 'ck', checkbox: true},
                {field: 'id', title: 'id', hidden: true},
                {
                    field: 'name',
                    title: '地名',
                    width: 200,
                    halign: 'center',
                    align: 'center',
                    editor: 'textbox',
                    // fixed: true
                },
                {
                    field: 'translation',
                    title: '翻译',
                    width: 200,
                    halign: 'center',
                    align: 'center',
                    editor: 'textbox',
                    // fixed: true
                },
                {
                    field: 'frequency',
                    title: '频率',
                    width: 200,
                    halign: 'center',
                    align: 'center',
                    editor: 'textbox',
                    // fixed: true
                },
                //{
                //    field: 'operate', title: '操作', width: 150, align: 'center',
                //    formatter: function (value, row, index) {
                //        return '<a href="#" style="color: #317ee8" onclick="APPVAR.mainMenu.m4.operaUserModify(' + index + ')">修改</a>' +
                //            '<a style="margin:0 5px; border-right: 1px solid #317ee8;"></a>' +
                //            '<a href="#" style="color: #ff4c4c" onclick="APPVAR.mainMenu.m4.operaUserDelete(' + index + ')">删除</a>'
                //    }
                //}
            ]],
            // toolbar: '#geTableToolbar',
            onBeforeLoad: function () {
                var $title = $('.panel-title');
                $title.html('<a style="margin:0 8px;border-right: 3px solid #317ee8;"></a>通名库');
            }
        });
    };
    var RulemanageTables = function () {
        $('#ruletablepanel').layout('resize');
        $('#dg3').datagrid({
            title: '规则库',
            rownumbers: true,
            singleSelect: false,
            autoRowHeight: false,
            pagination: true,
            pageSize: 50,
            pagePosition: 'bottom',
            fitColumns: true,
            striped: true,
            method: 'POST',
            url: '/getIpaInstance',
            queryParams: {
                start:1,
                end:100
            },

            columns: [[
                {field: 'ck', checkbox: true},
                {field: 'id', title: 'id', hidden: true},
                {
                    field: 'Phonogram',
                    title: '音标',
                    width: 300,
                    halign: 'center',
                    align: 'center',
                    editor: 'textbox',
                    // fixed: true
                },
                {
                    field: 'Chinese character',
                    title: '汉字',
                    width: 300,
                    halign: 'center',
                    align: 'center',
                    editor: 'textbox',
                    // fixed: true
                },
                //{
                //    field: 'operate', title: '操作', width: 150, align: 'center',
                //    formatter: function (value, row, index) {
                //        return '<a href="#" style="color: #317ee8" onclick="APPVAR.mainMenu.m4.operaUserModify(' + index + ')">修改</a>' +
                //            '<a style="margin:0 5px; border-right: 1px solid #317ee8;"></a>' +
                //            '<a href="#" style="color: #ff4c4c" onclick="APPVAR.mainMenu.m4.operaUserDelete(' + index + ')">删除</a>'
                //    }
                //}
            ]],
            // toolbar: '#ruleTableToolbar',
            onBeforeLoad: function () {
                var $title = $('.panel-title');
                $title.html('<a style="margin:0 8px;border-right: 3px solid #317ee8;"></a>规则库');
            }
        });
    };







    $('#btnSpAdd').click(function () {
        //console.log("添加用户");
        //alert("哈哈");
        // 弹出详细信息修改框

    });

}



