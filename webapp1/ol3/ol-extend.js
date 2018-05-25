window.app = {};
var app = window.app;

app.Tools = function(opt_options) {
    var options = opt_options || {};

    var element = document.createElement('div'),
        toolsHeader = document.createElement('div');
    element.className = 'tools-div ol-unselectable ol-control';
    toolsHeader.className = 'tools-header';

    if(options.headerIcon && options.headerLabel){
        toolsHeader.innerText = options.headerLabel;
        toolsHeader.style.backgroundImage = "url(" + options.headerIcon+ ")";
        toolsHeader.className += " tools-labelandicon";
    }else if(options.headerIcon){
        toolsHeader.style.backgroundImage = "url(" + options.headerIcon+ ")";
        toolsHeader.className += ' tools-icononly-header';
    }else if(options.headerLabel){
        toolsHeader.innerText = options.headerLabel;
        toolsHeader.className += ' tools-labelonly';
    }else{
        toolsHeader.innerText = "工具";
    }
    toolsHeader.title = "工具";

    element.appendChild(toolsHeader);

    var ul = document.createElement('ul'),
        liClassName = "tools-li ";
    ul.className = 'tools-ul';

    if(options.style == "horizontal"){
        toolsHeader.className += " tools-style-h";
        ul.className += " tools-style-h";
        liClassName += " tools-style-h tools-li-border-right";
    }else{
        toolsHeader.className += " tools-style-v";
        ul.className += " tools-style-v";
        liClassName += " tools-style-v";
    }

    toolsHeader.addEventListener("click",function(e){
        if(ul.style.display == "block"){
            $(ul).hide(300);
        }else {
            $(ul).show(300);
        }
    });

    for(var i = 0,size = options.items.length;i<size;i++){
        var li = document.createElement('li');
        if(options.items[i].label && options.items[i].icon){
            li.className = liClassName + " tools-labelandicon";
            li.innerText = options.items[i].label;
            li.style.backgroundImage = "url(" + options.items[i].icon + ")";
            li.style.backgroundRepeat="no-repeat";
        }else if(options.items[i].label){
            li.className = liClassName + " tools-labelonly";
            li.innerText = options.items[i].label;
        }else if(options.items[i].icon){
            li.className = liClassName + " tools-icononly";
            li.style.backgroundImage = "url(" + options.items[i].icon + ")";
            li.style.backgroundRepeat="no-repeat";
            if(options.items[i].title){
                li.title = options.items[i].title;
            }
        }

        if(options.items[i].visible || options.items[i].visible == undefined){
            li.style.display = 'block';
        }else{
            li.style.display = 'none';
        }

        var func = options.items[i].func;
        if(func){
            li.addEventListener("click",func);
        }
        ul.appendChild(li);
    }
    element.appendChild(ul);
    //element.addEventListener("mouseover",function(e){
    //        ul.style.display = "block";
    //});
    //element.addEventListener("mouseout",function(e){
    //        ul.style.display = "none";
    //});

    this.showItemByIndex = function(index){
        $(ul).find("li").eq(index).show();
    }

    this.hideItemByIndex = function(index){
        $(ul).find("li").eq(index).hide();
    }

    this.addItem = function(data){
        var li = document.createElement('li');
        if(data.label && data.icon){
            li.className = liClassName + " tools-labelandicon";
            li.innerText = data.label;
            li.style.backgroundImage = "url(" + data.icon + ")";
            li.style.backgroundRepeat="no-repeat";
        }else if(data.label){
            li.className = liClassName + " tools-labelonly";
            li.innerText = data.label;
        }else if(data.icon){
            li.className = liClassName + " tools-icononly";
            li.style.backgroundImage = "url(" + data.icon + ")";
            li.style.backgroundRepeat="no-repeat";
        }

        if(data.visible || data.visible == undefined){
            li.style.display = 'block';
        }else{
            li.style.display = 'none';
        }

        var func = data.func;
        if(func){
            li.addEventListener("click",func);
        }
        ul.appendChild(li);
    }

    this.removeItemByIndex = function(index){
        $(ul).find("li").eq(index).remove();
    }

    ol.control.Control.call(this, {
        element: element,
        target: options.target
    });
};
ol.inherits(app.Tools, ol.control.Control);

app.SelectNoStyle = function(opt_options){
    ol.interaction.Interaction.call(this, {
        handleEvent: this.handleEvent,
    });

    var options = opt_options || {};

    this.deepSelect_ = (typeof(options.deepSelect) == 'boolean') ? options.deepSelect : false;
    this.condition_ = (typeof(options.condition) == 'function') ? options.condition : ol.events.condition.singleClick;
    this.multiSelect_ = (typeof(options.multiSelect) == 'boolean') ? options.multiSelect : false;
    this.layerFilter_ = (typeof(options.layerFilter) == 'function') ? options.layerFilter: function(layer){return true};
    this.featureFilter_ = (typeof(options.featureFilter) == 'function') ? options.featureFilter: function(feature,layer){return true};

    var selected = new Array();
    var deselected = new Array();
    var postFunc = new Array();
    var selectChanged = false;
    var selectEvent ={
        selected: undefined,
        deselected: undefined,
        event: undefined
    };

    this.getSelectedFeatures = function(){
        return selected;
    }

    this.getDeselectedFeatures = function(){
        return deselected;
    }

    this.isSelectChanged = function() {
        return selectChanged;
    }

    this.isSelected = function(feature){
        var length = selected.length;

        for(var i=0; i<length; i++){
            if(feature === selected[i]){
                return true;
            }
        }

        return false;
    }

    this.isDeselected = function(feature){
        var length = deselected.length;

        for(var i=0; i<length; i++){
            if(feature === deselected[i]){
                return true;
            }
        }

        return false;
    }

    this.clearSelect = function(){
        deselected.splice(0);
        deselected = deselected.concat(selected);
        selected.splice(0);

        var length = deselected.length;
        for(var i=0; i<length; i++){
            deselected[i].changed();
        }

        selectEvent.event = undefined;
        selectEvent.selected = selected;
        selectEvent.deselected = deselected;

        var postFuncLength = postFunc.length;
        for(var i=0; i<postFuncLength; i++){
            postFunc[i](selectEvent);
        }
    }

    this.selectFeatureByCode = function(feature){
        if(!feature) return;

        deselected.splice(0);
        deselected = deselected.concat(selected);
        selected.splice(0);
        selected.push(feature);

        var length = selected.length;
        for(var i=0; i<length; i++){
            selected[i].changed();
        }

        length = deselected.length;
        for(var i=0; i<length; i++){
            deselected[i].changed();
        }

        selectEvent.event = undefined;
        selectEvent.selected = selected;
        selectEvent.deselected = deselected;

        var postFuncLength = postFunc.length;
        for(var i=0; i<postFuncLength; i++){
            postFunc[i](selectEvent);
        }
    }

    this.onPostSelect = function(func){
        if(func){
            postFunc.push(func);
        }
    }

    this.handleEvent = function(mapBrowserEvent) {
        if (!this.condition_(mapBrowserEvent)) {
            return true;
        }

        var map = mapBrowserEvent.map;
        var selectedThis = [];
        var features;

        map.forEachFeatureAtPixel(mapBrowserEvent.pixel,
            function(feature, layer) {
                if (this.featureFilter_(feature, layer)) {
                    features = feature.get("features");
                    if(!features || features.length==1 || this.deepSelect_){
                        selectedThis.push(feature);
                    }
                    return !this.multiSelect_;
                }
            }, this, this.layerFilter_);

        deselected.splice(0);

        var isSelectedThis = false;
        var selectedThisLength = selectedThis.length;
        var selectedLastLength = selected.length;

        for(var i=0; i<selectedLastLength; i++){
            isSelectedThis = false;

            for(var j=0; j<selectedThisLength; j++){
                if(selectedThis[j] == selected[i]){
                    isSelectedThis = true;
                    break;
                }
            }

            if(!isSelectedThis){
                deselected.push(selected[i]);
                selectChanged = true;
            }
        };

        if(selectChanged || selectedThisLength != selectedLastLength){
            selectChanged = true;
            selected.splice(0);
            selected = selected.concat(selectedThis);
        }

        if (selectChanged) {
            var length = selected.length;
            for(var i=0; i<length; i++){
                selected[i].changed();
            }
            length = deselected.length;
            for(var i=0; i<length; i++){
                deselected[i].changed();
            }

            selectEvent.event = mapBrowserEvent;
            selectEvent.selected = selected;
            selectEvent.deselected = deselected;

            var postFuncLength = postFunc.length;
            for(var i=0; i<postFuncLength; i++){
                postFunc[i](selectEvent);
            }
        }

        return ol.events.condition.pointerMove(mapBrowserEvent);
    };
};
ol.inherits(app.SelectNoStyle, ol.interaction.Interaction);

ol.control.MapSwitcher = function(opt_options){
    var options = opt_options || {};

    var container = document.createElement('div');
    container.className = 'ol-mapswitcher';

    var txtType = document.createElement('div');
    txtType.innerHTML = '影像';
    txtType.className = 'maptype-text';

    container.appendChild(txtType);

    var ul = document.createElement('ul');
    ul.className = 'img-year-number';

    ul.innerHTML = [
        '<label class="img-label" for="radioImgLbl">'+
        '<input type="checkbox" id="radioImgLbl" class="radio-img-label" checked/>注记'+
        '</label>'].join("");

    container.appendChild(ul);

    //切换地图
    $(container).click(function (e) {
        if($(this).hasClass("vec-group")){
            $(this).removeClass("vec-group");
            TileLayerManager.switchMap(1);
            $(".img-year-number").hide();
            $(".maptype-text").text("影像");
        }else{
            $(this).addClass("vec-group");
            TileLayerManager.switchMap(2,true);
            $(".img-year-number").show();
            $(".maptype-text").text("矢量");
            $(".radio-img-label").prop("checked",true);
        }
    });

    $(ul).click(function(e){
        if (event.stopPropagation) {
            event.stopPropagation();
        }else if (window.event) {
            window.event.cancelBubble = true;
        }
    });

    $(ul).find(".radio-img-label").change(function(){
        if($(this).prop("checked")){
            var radioVal = $(".number_year.active").text();
            switchImg(2014,true);
        }else{
            var radioVal = $(".number_year.active").text();
            switchImg(2014,false);
        }
    });

    function switchImg(radioVal,flag){
        if (radioVal == "2014") {
            TileLayerManager.switchMap(2, flag);
        }
        else if (radioVal == "2013") {
            TileLayerManager.switchMap(3, flag);
        }
        else if (radioVal == "2012") {
            TileLayerManager.switchMap(4, flag);
        }
        else if (radioVal == "2008") {
            TileLayerManager.switchMap(5, flag);
        }
        else {
            TileLayerManager.switchMap(6, flag);
        }
    }

    ol.control.Control.call(this, {
        element: container,
        target: options.target
    });
};
ol.inherits(ol.control.MapSwitcher, ol.control.Control);