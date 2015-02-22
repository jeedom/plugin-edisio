<?php
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


if (!isConnect('admin')) {
    throw new Exception('401 Unauthorized');
}
if (config::byKey('enableLogging', 'edisio', 0) == 0) {
    echo '<div class="alert alert-danger">{{Vous n\'avez pas activé l\'enregistrement de tous les messages : allez dans Générale -> Plugin puis edisio et coché la case correspondante}}</div>';
}
?>
<div class="alert alert-warning">{{Pensez bien à activer l'écriture de tous les messages dans la configuration du plugin et à redémarrer le démon une fois cela fait (N'oubliez pas de tout désactiver une fois fini)}}</div>
<pre id='pre_edisiolog' style='overflow: auto; height: 95%;with:90%;'></pre>


<script>
    getRfxLog(1);

    function getRfxLog(_autoUpdate) {
        $.ajax({
            type: 'POST',
            url: 'core/ajax/log.ajax.php',
            data: {
                action: 'get',
                logfile: 'edisiocmd.message',
            },
            dataType: 'json',
            global: false,
            error: function(request, status, error) {
                setTimeout(function() {
                    getJeedomLog(_autoUpdate, _log)
                }, 1000);
            },
            success: function(data) {
                if (data.state != 'ok') {
                    $('#div_alert').showAlert({message: data.result, level: 'danger'});
                    return;
                }
                var log = '';
                var regex = /<br\s*[\/]?>/gi;
                for (var i in data.result.reverse()) {
                    log += data.result[i][2].replace(regex, "\n");
                }
                $('#pre_edisiolog').text(log);
                $('#pre_edisiolog').scrollTop($('#pre_edisiolog').height() + 200000);
                if (!$('#pre_edisiolog').is(':visible')) {
                    _autoUpdate = 0;
                }

                if (init(_autoUpdate, 0) == 1) {
                    setTimeout(function() {
                        getRfxLog(_autoUpdate)
                    }, 1000);
                }
            }
        });
    }

</script>