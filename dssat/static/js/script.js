 var map = L.map('map').setView([32.806671, -86.791130], 7);
var gcountry='';
var adm1='';
var admin1_geojson;

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

function load_charts(admin1){
    window.location.href=window.location.protocol
        +'//'+window.location.host
        +'/charts/'+admin1+'/';
}
function load_irrigation_charts(admin1){
    window.location.href=window.location.protocol
        +'//'+window.location.host
        +'/irrigation/'+admin1+'/';
}

function ajax_call(ajax_url, ajax_data) {
    //update database
    console.log(ajax_data);
    return $.ajax({
        type: "POST",
        headers: {'X-CSRFToken': getCookie('csrftoken')},
        url: ajax_url.replace(/\/?$/, '/'),
        dataType: "json",
        data: ajax_data
    })
        .fail(function (xhr, status, error) {
        });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
//
// ['#7f1a01', '#ac7726', '#c0eac3', '#2d88be', '#053399']
// Color from roma cmap https://www.fabiocrameri.ch/colourmaps-userguide/
// vik: ['#5b0108', '#b75a26', '#ebe6e2', '#116496', '#011462']
function getColor(d) {
    return d == 'Very Low' ? '#5b0108':
           d == 'Low' ? '#b75a26':
           d == 'Normal' ? "#ebe6e2":
           d == 'High' ? "#116496":
           d == 'Very High' ? "#011462":
           "#FFFFFF";
}

function yieldCatStyle(feature) {
    return {
        fillColor: getColor(feature.properties.pred_cat),
        weight: 2,
        opacity: 1,
        color: '#000000',
        // dashArray: '3',
        fillOpacity: 0.7
    }
}

function zoomToRegions(schema){
    var json_data={'schema':schema};
    var xhr = ajax_call('get-regions/',json_data);
    xhr.done(function(data){
        console.log(data);
        var geojson = L.geoJSON(
            data.rows,
            {
                onEachFeature: onEachFeature_regions,
                style: yieldCatStyle
            }
        ).addTo(map);
        admin1_geojson = geojson;
        console.log(admin1_geojson)
    });
}

// // Legend to be added when country is clicked
// var legend = L.control({position: 'topright'});
// legend.onAdd = function (map) {
//     var div = L.DomUtil.create('div', 'info legend'),
//         labels = ['Very Low', 'Low', 'Normal', 'High', 'Very High'];
//     // loop through our density intervals and generate a label with a colored square for each interval
//     div.innerHTML += '<h6>Legend</h6>'
//     for (var i = labels.length; i > 0; i--) {
//         div.innerHTML +=
//             '<i style="background:' + getColor(labels[i-1]) + '"></i> ' +
//             labels[i-1]  + '<br>';
//     }
//     return div;
// }
//
//
  zoomToRegions('alabama');
// // For countries feature

// For each admin1 layer
function whenClicked_region(e){
    console.log(e.target.feature)
    var admin1 = e.target.feature.properties.admin1;
    var predCat = e.target.feature.properties.pred_cat;
    var predVal = Math.round(e.target.feature.properties.pred);
    var nitroRate = Math.round(e.target.feature.properties.nitro_rate);
    var ureaRate = Math.round(e.target.feature.properties.urea_rate);
    var refPeriod = e.target.feature.properties.ref_period;
    var plantingPeriod = e.target.feature.properties.planting_p;
    var obsAvg = Math.round(e.target.feature.properties.obs_avg)
    var season = e.target.feature.properties.season_nam
    console.log(admin1);

    // var country = e.target.feature.properties.adm0_en;
    console.log(e.target.feature.properties);
    var str=[admin1,gcountry.toLowerCase().toString()].join('_');
    console.log(str)
    str="'"+str+"'";

    var popup = L.popup( {maxWidth: 'auto',
  minWidth: 500, // Optional lower limit
  autoPan: true});
    popup.setLatLng(e.latlng)
         .setContent(
             '<h4>'+admin1+'</h4>'

             + '<br><div class="d-flex justify-content-between w-100"><center><button id="charts" class="btn btn-secondary"'
             + 'style="font-weight: bold; background: green"'
             + ' onclick="load_charts('+str+')">Sensitivity Analysis</button>'
               + '&nbsp<button id="irrigation_charts" class="btn btn-secondary"'
             + 'style="font-weight: bold; background: green"'
             + ' onclick="load_irrigation_charts('+str+')">Irrigation Analysis</button></center></div>'
             )
        .openOn(map);
}

var info = L.control();

info.onAdd = function (map) {
    this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
    this.update();
    return this._div;
};

// method that we will use to update the control based on feature properties passed
info.update = function (props) {
    this._div.innerHTML = '<h6>Average forecasted yield</h6>' +  (props ?
        '<b>' + props.admin1 + '</b><br />' + props.season_nam + ' season <br>'
        + Math.round(props.pred) + ' kg/ha'
        : 'Hover over a county');
};

function highlightFeature(e) {
    var layer = e.target;
    layer.setStyle({
        weight: 5,
        color: '#8c8c8c',
        dashArray: '',
        fillOpacity: 0.7
    });
    layer.bringToFront();
    info.update(layer.feature.properties);
}

function resetHighlight(e) {
    admin1_geojson.resetStyle(e.target);
    info.update();
}

// For admin1 features
function onEachFeature_regions(feature, layer) {
    layer.on({
        click: whenClicked_region,
        mouseover: highlightFeature,
        mouseout: resetHighlight
    })
}


