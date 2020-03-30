function initMap(){

    ROOT = window.location.origin;

    radius = 20, zoom = 14;
    var dublin_downtown = {
      lat:53.346763,
      lng:-6.2568436
    };

    var mapDefault = {
        center: dublin_downtown,
        zoom: 13,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };

    map = new google.maps.Map(document.getElementById('map'), mapDefault);

    var bikeLayer = new google.maps.BicyclingLayer();
    bikeLayer.setMap(map);

    showAllStationMarkers();

    dropdownStationMenu();

}

function showAllStationMarkers(){
    var url_static = "http://localhost:5000/stations";
    var url_dynamic = "http://localhost:5000/available";

    $.when(
        $.getJSON(url_static),
        $.getJSON(url_dynamic)
    ).done(function(data1, data2){
        var parse1 = data1[0];
        var parse2 = data2[0];
        //console.log(parse1);
        //console.log(parse2);
        if("stations" in parse1 && "available" in parse2){
            var stations = parse1.stations;
            var available = parse2.available;
            _.forEach(stations, function(station){
                //console.log('station', station.number);
                _.forEach(available, function(avail){
                    //console.log('avail', avail.number);
                    if(station.number == avail.number){
                        var available_bikes = avail.available_bikes;
                        var available_bike_stands = avail.available_bike_stands;
                        var url;
                        if(available_bikes <= 3){
                            url = "http://maps.google.com/mapfiles/ms/icons/red-dot.png";
                        }else if(available_bikes <= 10){
                            url = "http://maps.google.com/mapfiles/ms/icons/yellow-dot.png";
                        }else{
                            url = "http://maps.google.com/mapfiles/ms/icons/green-dot.png";
                        }
                        var marker = new google.maps.Marker({
                            map: map,
                            position:{
                                lat:parseFloat(station.latitude),
                                lng:parseFloat(station.longitude)
                            },
                            icon:{
                                url:url
                            }
                        });
                        map.setCenter(marker.getPosition());

                        var content = "<p>Bike Station: "+station.name+"</p><p>Available bike stands: "+available_bike_stands+"</p><p>Available bikes: "+available_bikes+"</p>";
                        var infowindow = new google.maps.InfoWindow({maxWidth: 220});


                        google.maps.event.addListener(marker,'click', (function(marker,content,infowindow){
                            return function() {
                                infowindow.setContent(content);
                                infowindow.open(map,marker);
                            };
                        })(marker,content,infowindow));

                        google.maps.event.addListener(map, 'click', function () {
                            infowindow.close();
                        });

                    }
                })


            })
        }
    });
}

function dropdownStationMenu(){
    var selectPickUpStation = "<select id=pickupstation>";
    var selectDropOffStation = "<select id=dropoffstation>";
    selectPickUpStation += "<option value=" + 'selStation' + ">" + 'Select Pick Up Station:' + "</option>"
    selectDropOffStation += "<option value=" + 'selStation' + ">" + 'Select Drop Off Station:' + "</option>"
    $.getJSON("http://localhost:5000/stations", function(data){
        if("stations" in data){
            var stations = data.stations;
            _.forEach(stations, function(station){
                selectPickUpStation += "<option value=\"" + station.number + "\">" + station.name + "</option>"
                selectDropOffStation += "<option value=\"" + station.number + "\">" + station.name + "</option>"
            })
            selectPickUpStation += "</select>";
            selectDropOffStation += "</select>";
        }

        document.getElementById("pickUpStation").innerHTML = selectPickUpStation;
        document.getElementById("dropOffStation").innerHTML = selectDropOffStation;
    });
}

function onclickSubmit(){
    var currentDate = new Date();
    var currentTimestamp = currentDate.getTime()/1000;
    console.log(currentTimestamp);
    var pickup = document.getElementById("pickupstation");
    var pickupValue = pickup.options[pickup.selectedIndex].value;

    var dropoff = document.getElementById("dropoffstation");
    var dropoffValue = dropoff.options[dropoff.selectedIndex].value;

    url_pickup = "http://localhost:5000/available/" + pickupValue;
    url_dropoff = "http://localhost:5000/available/" + dropoffValue;

    console.log(url_pickup);

    $.when(
        $.getJSON(url_pickup),
        $.getJSON(url_dropoff)
    ).done(function(data1, data2){
        var parse1 = data1[0];
        var parse2 = data2[0];
        if("availableid" in parse1 && "availableid" in parse2){
            var pickupInfo = parse1.availableid;
            var dropoffInfo = parse2.availableid;
            var DailyArray = [];
            _.forEach(pickupInfo, function(pickupInfoElem){
                var dateRegexp = /(?<day>[0-9]{2})-(?<month>[a-zA-Z]{3})-(?<year>[0-9]{4})/;
                var timeRegexp = /(?<hour>[0-9]{2}):(?<minute>[0-9]{2}):(?<second>[0-9]{2})/;
                var pickupdatetime = pickupInfoElem.datetime;
                var pickupdate = pickupdatetime.match(dateRegexp).groups;
                var pickuptime = pickupdatetime.match(timeRegexp).groups;

                IntMonth = monthStringToInt(pickupdate.month);

                TimestampElem = toTimestamp(pickupdate.year, IntMonth, pickupdate.day, pickuptime.hour, pickuptime.minute, pickuptime.second);
                console.log(TimestampElem);
                if((currentTimestamp - TimestampElem)<86400){
                    DailyArray.push([new Date(parseInt(pickupdate.year), parseInt(IntMonth)-1, parseInt(pickupdate.day), parseInt(pickuptime.hour), parseInt(pickuptime.minute), parseInt(pickuptime.second)),pickupInfoElem.available_bikes])
                }

            })

            google.charts.load("visualization", "1", {packages:['corechart', 'bar']});
            google.setOnLoadCallback(function() { drawDailyChart(DailyArray); });
        }
    });
}

function toTimestamp(year,month,day,hour,minute,second){
    // To get the timestamp in second.
    // One day 86400 seconds.
    // One week 604800 seconds.
    var Timestamp = new Date(Date.UTC(year,month-1,day,hour,minute,second));
    return Timestamp.getTime()/1000;
}

function monthStringToInt(string){
    // Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec.
    var num;
    switch (string) {
        case "Jan":
            num = 1;
            break;
        case "Feb":
            num = 2;
            break;
        case "Mar":
            num = 3;
            break;
        case "Apr":
            num = 4;
            break;
        case "May":
            num = 5;
            break;
        case "Jun":
            num = 6;
            break;
        case "Jul":
            num = 7;
            break;
        case "Aug":
            num = 8;
            break;
        case "Sep":
            num = 9;
            break;
        case "Oct":
            num = 10;
            break;
        case "Nov":
            num = 11;
            break;
        case "Dec":
            num = 12;
            break;
      }
    return num;
}


function drawDailyChart(DailyArray) {

    var data = new google.visualization.DataTable();
    data.addColumn('datetime', 'Time of Day');
    data.addColumn('number', 'available bikes');

    console.log(DailyArray);
    data.addRows(DailyArray.reverse());

    var options = {
      title: 'Total Available Bikes Throughout the Day',
      height: 450
    };

    var chart = new google.charts.Bar(document.getElementById('chart_div'));

    chart.draw(data, google.charts.Bar.convertOptions(options));
  }