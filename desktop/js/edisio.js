
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
    $('.eqLogicAttr[data-l1key=status][data-l2key=battery]').on('change', function () {
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
 $('#bt_healthEdisio').on('click', function () {
    $('#md_modal').dialog({title: "{{Santé Edisio}}"});
    $('#md_modal').load('index.php?v=d&plugin=edisio&modal=health').dialog('open');
});
 $("#table_cmd").sortable({axis: "y", cursor: "move", items: ".cmd", placeholder: "ui-state-highlight", tolerance: "intersect", forcePlaceholderSize: true});


 function getModelList(_conf,_id) {
    $.ajax({
        type: "POST", 
        url: "plugins/edisio/core/ajax/edisio.ajax.php", 
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
        success: function (data) {
            if (data.state != 'ok') {
                $('#div_alert').showAlert({message: data.result, level: 'danger'});
                return;
            }
            var options = '';
            var options = '';
            for (var i in data.result) {
                if (data.result[i]['selected'] == 1){
                    options += '<option value="'+i+'" selected>'+data.result[i]['value']+'</option>';
                } else {
                    options += '<option value="'+i+'">'+data.result[i]['value']+'</option>';
                }
            }
            $(".modelList").show();
            $(".listModel").html(options);
            $icon = $('.eqLogicAttr[data-l1key=configuration][data-l2key=iconModel]').value();
            if($icon != '' && $icon != null){
                $('#img_device').attr("src", 'plugins/edisio/core/config/devices/'+$icon+'.jpg');
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
    tr += '<select class="cmdAttr form-control input-sm" data-l1key="value" style="display : none;margin-top : 5px;" title="La valeur de la commande vaut par défaut la commande">';
    tr += '<option value="">Aucune</option>';
    tr += '</select>';
    tr += '</td>';
    tr += '<td>';
    tr += '<input class="cmdAttr form-control input-sm" data-l1key="id" style="display : none;">';
    tr += '<span class="type" type="' + init(_cmd.type) + '">' + jeedom.cmd.availableType() + '</span>';
    tr += '<span class="subType" subType="' + init(_cmd.subType) + '"></span>';
    tr += '</td>';
    tr += '<td><input class="cmdAttr form-control input-sm" data-l1key="logicalId" value="0">';
    tr += '<input class="cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="id" placeholder="{{ID}}" style="margin-top : 5px;margin-right:2px;width:24%;display:inline-block;">';
    tr += ' <input class="cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="group" style="width : 20%; display : inline-block;margin-right : 5px;margin-top : 5px;" placeholder="{{Groupe}}">';
    tr += '<input class="cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="returnStateValue" placeholder="{{Valeur retour d\'état}}" style="width : 20%; display : inline-block;margin-top : 5px;margin-right : 5px;">';
    tr += '<input class="cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="returnStateTime" placeholder="{{Durée avant retour d\'état (min)}}" style="width : 20%; display : inline-block;margin-top : 5px;">';
    tr += '</td>';
    tr += '<td>';
    tr += '<span><label class="checkbox-inline"><input type="checkbox" class="cmdAttr checkbox-inline" data-l1key="isHistorized" checked/>{{Historiser}}</label></span> ';
    tr += '<span><label class="checkbox-inline"><input type="checkbox" class="cmdAttr checkbox-inline" data-l1key="isVisible" checked/>{{Afficher}}</label></span> ';
    tr += '<span><label class="checkbox-inline"><input type="checkbox" class="cmdAttr" data-l1key="display" data-l2key="invertBinary"/>{{Inverser}}</label></span> ';
    tr += '</td>';
    tr += '<td>';
    tr += '<select class="cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="updateCmdId" style="display : none;margin-top : 5px;" title="Commande d\'information à mettre à jour">';
    tr += '<option value="">Aucune</option>';
    tr += '</select>';
    tr += '<input class="cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="updateCmdToValue" placeholder="Valeur de l\'information" style="display : none;margin-top : 5px;">';
    tr += '<input class="cmdAttr form-control input-sm" data-l1key="unite"  style="width : 100px;" placeholder="Unité" title="Unité">';
    tr += '<input class="cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="minValue" placeholder="Min" title="Min"> ';
    tr += '<input class="cmdAttr form-control input-sm" data-l1key="configuration" data-l2key="maxValue" placeholder="Max" title="Max" style="margin-top : 5px;">';
    tr += '</td>';
    tr += '<td>';
    if (is_numeric(_cmd.id)) {
        tr += '<a class="btn btn-default btn-xs cmdAction" data-action="configure"><i class="fa fa-cogs"></i></a> ';
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

$('.changeIncludeState').on('click', function () {
   $.ajax({
    type: "POST", 
    url: "plugins/edisio/core/ajax/edisio.ajax.php", 
    data: {
        action: "changeIncludeState",
        state: $(this).attr('data-state')
    },
    dataType: 'json',
    error: function (request, status, error) {
        handleAjaxError(request, status, error);
    },
    success: function (data) { 
        if (data.state != 'ok') {
            $('#div_alert').showAlert({message: data.result, level: 'danger'});
            return;
        }
    }
});
});

$('body').off('edisio::include_mode').on('edisio::include_mode', function (_event,_options) {
    if (_options['state'] == 1) {
        if($('.include').attr('data-state') != 0){
            $.hideAlert();
            $('.include:not(.card)').removeClass('btn-default').addClass('btn-success');
            $('.include').attr('data-state', 0);
            $('.include.card').css('background-color','#8000FF');
            $('.include.card span center').text('{{Arrêter l\'inclusion}}');
            $('.include:not(.card)').html('<i class="fa fa-sign-in fa-rotate-90"></i> {{Arreter inclusion}}');
            $('#div_inclusionAlert').showAlert({message: '{{Vous etes en mode inclusion. Recliquez sur le bouton d\'inclusion pour sortir de ce mode}}', level: 'warning'});
        }
    } else {
        if($('.include').attr('data-state') != 1){
            $.hideAlert();
            $('.include:not(.card)').addClass('btn-default').removeClass('btn-success btn-danger');
            $('.include').attr('data-state', 1);
            $('.include:not(.card)').html('<i class="fa fa-sign-in fa-rotate-90"></i> {{Mode inclusion}}');
            $('.include.card span center').text('{{Mode inclusion}}');
            $('.include.card').css('background-color','#ffffff');
        }
    }
});

$('body').off('edisio::includeDevice').on('edisio::includeDevice', function (_event,_options) {
    if (modifyWithoutSave) {
        $('#div_inclusionAlert').showAlert({message: '{{Un périphérique vient d\'être inclu/exclu. Veuillez réactualiser la page}}', level: 'warning'});
    } else {
        if (_options == '') {
            window.location.reload();
        } else {
            window.location.href = 'index.php?v=d&p=edisio&m=edisio&id=' + _options;
        }
    }
});