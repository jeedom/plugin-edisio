
/* This file is part of Jeedom.
 *
 * Jeedom is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Jeedom is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Jeedom. If not, see <http://www.gnu.org/licenses/>.
 */

$(document).ready(function() {
$('.eqLogicAttr[data-l1key=configuration][data-l2key=device]').on('change', function () {
  if($('.li_eqLogic.active').attr('data-eqlogic_id') != ''){
    getModelList($(this).value(),$('.li_eqLogic.active').attr('data-eqlogic_id'));
    $('#img_device').attr("src", 'plugins/edisio/core/config/devices/'+$(this).value()+'.jpg');
}else{
    $('#img_device').attr("src",'plugins/edisio/doc/images/edisio_icon.png');
}  
});
 $('.eqLogicAttr[data-l1key=configuration][data-l2key=batteryStatus]').on('change', function () {
  if($(this).html() != ''){
    $('.hasBatterie').show();
}else{
    $('.hasBatterie').hide();
}
});

 $('.eqLogicAttr[data-l1key=status][data-l2key=lastCommunication]').on('change', function () {
  if($(this).html() != ''){
    $('.hasCommunication').show();
}else{
    $('.hasCommunication').hide();
}
});

 $('.eqLogicAttr[data-l1key=configuration][data-l2key=iconModel]').on('change', function () {
  if($(this).value() != '' && $(this).value() != null){
    $('#img_device').attr("src", 'plugins/edisio/core/config/devices/'+$(this).value()+'.jpg');
  }
});
});
 $("#table_cmd").sortable({axis: "y", cursor: "move", items: ".cmd", placeholder: "ui-state-highlight", tolerance: "intersect", forcePlaceholderSize: true});

 function stopEDISIODeamon() {
    $.ajax({// fonction permettant de faire de l'ajax
        type: "POST", // methode de transmission des données au fichier php
        url: "plugins/edisio/core/ajax/edisio.ajax.php", // url du fichier php
        data: {
            action: "stopDeamon",
        },
        dataType: 'json',
        error: function (request, status, error) {
            handleAjaxError(request, status, error);
        },
        success: function (data) { // si l'appel a bien fonctionné
        if (data.state != 'ok') {
            $('#div_alert').showAlert({message: data.result, level: 'danger'});
            return;
        }
        $('#div_alert').showAlert({message: 'Le démon a été correctement arrêté : il se relancera automatiquement dans 1 minute', level: 'success'});
    }
});
}

function getModelList(_conf,_id) {
    $.ajax({// fonction permettant de faire de l'ajax
        type: "POST", // methode de transmission des données au fichier php
        url: "plugins/edisio/core/ajax/edisio.ajax.php", // url du fichier php
        data: {
            action: "getModelList",
            conf: _conf,
            id: _id,
        },
        dataType: 'json',
        global: false,
        error: function (request, status, error) {
            handleAjaxError(request, status, error);
        },
        success: function (data) { // si l'appel a bien fonctionné
        if (data.state != 'ok') {
            $('#div_alert').showAlert({message: data.result, level: 'danger'});
            return;
        }
        var options = '<option value="'+_conf+'">1 - Défaut</option>';
        var initImg = _conf;
        for (var i in data.result) {
                var value = data.result[i]['value'];
                var selected = data.result[i]['selected'];
                if (selected == 1){
                    initImg = i;
                    options += '<option value="'+i+'" selected>'+value+'</option>';
                } else {
                    options += '<option value="'+i+'">'+value+'</option>';
                }
        }
        if (options != '<option value="'+_conf+'">1 - Défaut</option>'){
            $(".modelList").show();
            $(".listModel").html(options);
            $('#img_device').attr("src", 'plugins/edisio/core/config/devices/'+initImg+'.jpg');
        } else {
            $(".listModel").html(options);
            $(".modelList").hide();
        }
        }
});
}

$('#table_cmd').delegate('.cmdAttr[data-l1key=type]','change',function(){
    if($(this).value() == 'info'){
     $(this).closest('.cmd').find('.cmdAttr[data-l1key=configuration][data-l2key=group]').hide();
 }else{
     $(this).closest('.cmd').find('.cmdAttr[data-l1key=configuration][data-l2key=group]').show();
 }
});

$('body').delegate('.cmd .cmdAttr[data-l1key=type]', 'change', function () {
    if ($(this).value() == 'action') {
        $(this).closest('.cmd').find('.cmdAttr[data-l1key=configuration][data-l2key=id]').show();
        $(this).closest('.cmd').find('.cmdAttr[data-l1key=configuration][data-l2key=group]').show();
    } else {
        $(this).closest('.cmd').find('.cmdAttr[data-l1key=configuration][data-l2key=id]').hide();
        $(this).closest('.cmd').find('.cmdAttr[data-l1key=configuration][data-l2key=group]').hide();
    }
});


function addCmdToTable(_cmd) {
    if (!isset(_cmd)) {
        var _cmd = {configuration: {}};
    }

    var tr = '<tr class="cmd" data-cmd_id="' + init(_cmd.id) + '">';
    tr += '<td>';
    tr += '<div class="row">';
    tr += '<div class="col-sm-6">';
    tr += '<a class="cmdAction btn btn-default btn-sm" data-l1key="chooseIcon"><i class="fa fa-flag"></i> Icone</a>';
    tr += '<span class="cmdAttr" data-l1key="display" data-l2key="icon" style="margin-left : 10px;"></span>';
    tr += '</div>';
    tr += '<div class="col-sm-6">';
    tr += '<input class="cmdAttr form-control input-sm" data-l1key="name">';
    tr += '</div>';
    tr += '</div>';
    tr += '<select class="cmdAttr form-control tooltips input-sm" data-l1key="value" style="display : none;margin-top : 5px;" title="La valeur de la commande vaut par défaut la commande">';
    tr += '<option value="">Aucune</option>';
    tr += '</select>';
    tr += '</td>';
    tr += '<td class="expertModeVisible">';
    tr += '<input class="cmdAttr form-control input-sm" data-l1key="id" style="display : none;">';
    tr += '<span class="type" type="' + init(_cmd.type) + '">' + jeedom.cmd.availableType() + '</span>';
    tr += '<span class="subType" subType="' + init(_cmd.subType) + '"></span>';
    tr += '</td>';
    tr += '<td class="expertModeVisible"><input class="cmdAttr form-control input-sm" data-l1key="logicalId" value="0">';
    tr += '<input class="cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="id" placeholder="{{ID}}" style="margin-top : 5px;margin-right:2px;width:24%;display:inline-block;">';
    tr += ' <input class="cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="group" style="width : 20%; display : inline-block;margin-right : 5px;margin-top : 5px;" placeholder="{{Groupe}}">';
    tr += '<input class="cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="returnStateValue" placeholder="{{Valeur retour d\'état}}" style="width : 20%; display : inline-block;margin-top : 5px;margin-right : 5px;">';
    tr += '<input class="cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="returnStateTime" placeholder="{{Durée avant retour d\'état (min)}}" style="width : 20%; display : inline-block;margin-top : 5px;">';
    tr += '</td>';
    tr += '<td>';
    tr += '<span><input type="checkbox" class="cmdAttr bootstrapSwitch" data-l1key="isHistorized" data-label-text="{{Historiser}}" data-size="mini" /></span> ';
    tr += '<span><input type="checkbox" class="cmdAttr bootstrapSwitch" data-l1key="isVisible" data-label-text="{{Afficher}}" data-size="mini" checked/></span> ';
    tr += '<span><input type="checkbox" class="cmdAttr bootstrapSwitch expertModeVisible" data-label-text="{{Inverser}}" data-l1key="display" data-l2key="invertBinary" data-size="mini"/></span> ';
    tr += '</td>';
    tr += '<td>';
    tr += '<select class="cmdAttr form-control tooltips input-sm" data-l1key="configuration" data-l2key="updateCmdId" style="display : none;margin-top : 5px;" title="Commande d\'information à mettre à jour">';
    tr += '<option value="">Aucune</option>';
    tr += '</select>';
    tr += '<input class="tooltips cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="updateCmdToValue" placeholder="Valeur de l\'information" style="display : none;margin-top : 5px;">';
    tr += '<input class="cmdAttr form-control tooltips input-sm" data-l1key="unite"  style="width : 100px;" placeholder="Unité" title="Unité">';
    tr += '<input class="tooltips cmdAttr form-control input-sm expertModeVisible" data-l1key="configuration" data-l2key="minValue" placeholder="Min" title="Min"> ';
    tr += '<input class="tooltips cmdAttr form-control input-sm expertModeVisible" data-l1key="configuration" data-l2key="maxValue" placeholder="Max" title="Max" style="margin-top : 5px;">';
    tr += '</td>';
    tr += '<td>';
    if (is_numeric(_cmd.id)) {
        tr += '<a class="btn btn-default btn-xs cmdAction expertModeVisible" data-action="configure"><i class="fa fa-cogs"></i></a> ';
        tr += '<a class="btn btn-default btn-xs cmdAction" data-action="test"><i class="fa fa-rss"></i> Tester</a>';
    }
    tr += '<i class="fa fa-minus-circle pull-right cmdAction cursor" data-action="remove"></i></td>';
    tr += '</tr>';
    $('#table_cmd tbody').append(tr);
    var tr = $('#table_cmd tbody tr:last');
    jeedom.eqLogic.builSelectCmd({
        id: $(".li_eqLogic.active").attr('data-eqLogic_id'),
        filter: {type: 'info'},
        error: function (error) {
            $('#div_alert').showAlert({message: error.message, level: 'danger'});
        },
        success: function (result) {
            tr.find('.cmdAttr[data-l1key=value]').append(result);
            tr.find('.cmdAttr[data-l1key=configuration][data-l2key=updateCmdId]').append(result);
            tr.setValues(_cmd, '.cmdAttr');
            jeedom.cmd.changeType(tr, init(_cmd.subType));
        }
    });
}
