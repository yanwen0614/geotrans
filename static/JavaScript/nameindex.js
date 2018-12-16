/**
 * Created by casm on 2018/4/25.
 */
$(function () {


    //创建地图
    $(function () {
        //var Geamap = new Geocoder();
        $('#coordinatebutton').on('click', function () {
            var str = document.getElementById("coordinateinput").value;
            alert(str);
        });

            var arr = [104.293175, 35.7];
            var rome = new ol.Feature({
                geometry: new ol.geom.Point(ol.proj.fromLonLat(arr))
            });
            rome.setStyle(new ol.style.Style({
                image: new ol.style.Icon({
                    crossOrigin: 'anonymous',
                    src: 'images/map/marker-icon-green.png'
                })
            }));
            var vectorSource = new ol.source.Vector({
                features: [rome]
            });
            var vectorLayer = new ol.layer.Vector({
                source: vectorSource
            });
        var scaleLineControl = new ol.control.ScaleLine();
        //设置中心
        var coor = ol.proj.transform([104.293175, 35.7], 'EPSG:4326', 'EPSG:3857');
        var view = new ol.View({

            center: coor,
            zoom: 4,
            minZoom: 2,
            maxZoom: 17
        });
        var map = new ol.Map({
            //容器
            target: 'mapDiv',
            //图层
            layers: [
                new ol.layer.Tile({
                    source: new ol.source.XYZ({
                        title: "天地图路网",
                        url: "http://t2.tianditu.com/DataServer?T=vec_w&x={x}&y={y}&l={z}"
                    })
                }),
                new ol.layer.Tile({
                    source: new ol.source.XYZ({
                        title: "天地图文字标注",
                        url: "http://t2.tianditu.com/DataServer?T=cva_w&x={x}&y={y}&l={z}"
                    })
                }),
                vectorLayer

                /* new ol.layer.Tile({
                 title: "天地图卫星影像",
                 source: new ol.source.XYZ({
                 url: "http://t3.tianditu.com/DataServer?T=img_w&x={x}&y={y}&l={z}"
                 })
                 }) */
            ],
            //视图中心和缩放等级
            view: view,
            //比例尺
            controls: ol.control.defaults({
                attributionOptions: {
                    collapsible: false
                }
            }).extend([
                scaleLineControl
                //new ol.control.FullScreen()
            ])

        });
        ol.geom.Polygon()
    })

    //调节地图形状
    $('#mapDiv').css('height', $('#centerpanel').css('height'));
    $('#mapDiv').resize();


    // 单点翻译动态操作.js
    var A=Singlepointtranslation();
    //批量翻译动态操作.js
    var B=Batchtranslation();
    //系统管理动态操作.js
    var C =Systemmanage();

    //切换页面
    $('.menu1').on('click', function () {
        $('#menu1Page').css('display', 'block');
        $('#menu2Page').css('display', 'none');
        $('#menu3Page').css('display', 'none');
        $('#mapDiv').css('display', 'block');

        $('.btnLeftSel1').css('background-color', '#317ee8');
        $('.btnLeftSel2').css('background-color', '#2667b3');
        $('.btnLeftSel3').css('background-color', '#2667b3');

        //改变子菜单宽度
        UtilsFunc.changeMenuPanel(3);

        //调节地图变形
        $('#mapDiv').css('height', $('#centerpanel').css('height'));
        $('#mapDiv').resize();

    });
    $('.menu2').on('click', function () {
        $('#menu1Page').css('display', 'none');
        $('#menu2Page').css('display', 'block');
        $('#menu3Page').css('display', 'none');
        $('#mapDiv').css('display', 'block');

        $('.btnLeftSel1').css('background-color', '#2667b3');
        $('.btnLeftSel2').css('background-color', '#317ee8');
        $('.btnLeftSel3').css('background-color', '#2667b3');

        //改变子菜单宽度
        UtilsFunc.changeMenuPanel(2);

        //调节地图变形
        $('#mapDiv').css('height', $('#centerpanel').css('height'));
        $('#mapDiv').resize();


    });
    $('.menu3').on('click', function () {
        $('#menu1Page').css('display', 'none');
        $('#menu2Page').css('display', 'none');
        $('#menu3Page').css('display', 'block');
        $('#mapDiv').css('display', 'none');

        $('.btnLeftSel1').css('background-color', '#2667b3');
        $('.btnLeftSel2').css('background-color', '#2667b3');
        $('.btnLeftSel3').css('background-color', '#317ee8');

        //改变子菜单宽度
        UtilsFunc.changeMenuPanel(2);

        //调节地图变形
        $('#centerpanel').css('height', $('#centerpanel').css('height'));
        $('#centerpanel').resize();

        var mm =$('#btnSpecialManage').click();
    });
    //系统管理二级子菜单样式
    $('#btnSpecialManage').hover(function(evt) {
        $(this).css('background-image', "url('images/menu4/feedback-selected.png')");
        $(this).find("label").css('color', '#007DF0');
    }, function(evt) {
        if ($('#sptablepanel').css('display') == 'none') {
            $(this).css('background-image', "url('images/menu4/feedback.png')");
            $(this).find("label").css('color', '');
        }
    });
    $('#btnGeneralManage').hover(function(evt) {
        $(this).css('background-image', "url('images/menu4/feedback-selected.png')");
        $(this).find("label").css('color', '#007DF0');
    }, function(evt) {
        if ($('#getablepanel').css('display') == 'none') {
            $(this).css('background-image', "url('images/menu4/feedback.png')");
            $(this).find("label").css('color', '');
        }
    });
    $('#btnRuleManage').hover(function(evt) {
        $(this).css('background-image', "url('images/menu4/feedback-selected.png')");
        $(this).find("label").css('color', '#007DF0');
    }, function(evt) {
        if ($('#ruletablepanel').css('display') == 'none') {
            $(this).css('background-image', "url('images/menu4/feedback.png')");
            $(this).find("label").css('color', '#007DF0');
        }
    });

    // 工具函数
    var UtilsFunc = {};


    /**
     * 设置子菜单panel显示宽度
     * @param showType 分为两类：1：420px; 2: 650px;
     */
    UtilsFunc.changeMenuPanel = function (showType) {
        var $centerpanel = $('#centerpanel'),
            $westPanel = $('#leftpanel');
        // 总宽度
        var totalWidth = 1028;
        switch (showType) {

            case 1:
                if ($westPanel.panel('options').width != 90) {
                    $westPanel.panel('resize', {width: 90});
                    $centerpanel.panel('resize', {width: totalWidth - 90});
                }

                break;
            case 2:
                if ($westPanel.panel('options').width != 420) {
                    $westPanel.panel('resize', {width: 420});
                    $centerpanel.panel('resize', {width: totalWidth - 420});
                }

                break;

            case 3:
                if ($westPanel.panel('options').width != 650) {
                    $westPanel.panel('resize', {width: 650});
                    $centerpanel.panel('resize', {width: totalWidth - 650});
                }

                break;

            default:
                break;
        }
    }


})