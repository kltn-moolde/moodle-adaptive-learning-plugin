/*
   Licensed to the Apache Software Foundation (ASF) under one or more
   contributor license agreements.  See the NOTICE file distributed with
   this work for additional information regarding copyright ownership.
   The ASF licenses this file to You under the Apache License, Version 2.0
   (the "License"); you may not use this file except in compliance with
   the License.  You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/
var showControllersOnly = false;
var seriesFilter = "";
var filtersOnlySampleSeries = true;

/*
 * Add header in statistics table to group metrics by category
 * format
 *
 */
function summaryTableHeader(header) {
    var newRow = header.insertRow(-1);
    newRow.className = "tablesorter-no-sort";
    var cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 1;
    cell.innerHTML = "Requests";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 3;
    cell.innerHTML = "Executions";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 7;
    cell.innerHTML = "Response Times (ms)";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 1;
    cell.innerHTML = "Throughput";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 2;
    cell.innerHTML = "Network (KB/sec)";
    newRow.appendChild(cell);
}

/*
 * Populates the table identified by id parameter with the specified data and
 * format
 *
 */
function createTable(table, info, formatter, defaultSorts, seriesIndex, headerCreator) {
    var tableRef = table[0];

    // Create header and populate it with data.titles array
    var header = tableRef.createTHead();

    // Call callback is available
    if(headerCreator) {
        headerCreator(header);
    }

    var newRow = header.insertRow(-1);
    for (var index = 0; index < info.titles.length; index++) {
        var cell = document.createElement('th');
        cell.innerHTML = info.titles[index];
        newRow.appendChild(cell);
    }

    var tBody;

    // Create overall body if defined
    if(info.overall){
        tBody = document.createElement('tbody');
        tBody.className = "tablesorter-no-sort";
        tableRef.appendChild(tBody);
        var newRow = tBody.insertRow(-1);
        var data = info.overall.data;
        for(var index=0;index < data.length; index++){
            var cell = newRow.insertCell(-1);
            cell.innerHTML = formatter ? formatter(index, data[index]): data[index];
        }
    }

    // Create regular body
    tBody = document.createElement('tbody');
    tableRef.appendChild(tBody);

    var regexp;
    if(seriesFilter) {
        regexp = new RegExp(seriesFilter, 'i');
    }
    // Populate body with data.items array
    for(var index=0; index < info.items.length; index++){
        var item = info.items[index];
        if((!regexp || filtersOnlySampleSeries && !info.supportsControllersDiscrimination || regexp.test(item.data[seriesIndex]))
                &&
                (!showControllersOnly || !info.supportsControllersDiscrimination || item.isController)){
            if(item.data.length > 0) {
                var newRow = tBody.insertRow(-1);
                for(var col=0; col < item.data.length; col++){
                    var cell = newRow.insertCell(-1);
                    cell.innerHTML = formatter ? formatter(col, item.data[col]) : item.data[col];
                }
            }
        }
    }

    // Add support of columns sort
    table.tablesorter({sortList : defaultSorts});
}

$(document).ready(function() {

    // Customize table sorter default options
    $.extend( $.tablesorter.defaults, {
        theme: 'blue',
        cssInfoBlock: "tablesorter-no-sort",
        widthFixed: true,
        widgets: ['zebra']
    });

    var data = {"OkPercent": 100.0, "KoPercent": 0.0};
    var dataset = [
        {
            "label" : "FAIL",
            "data" : data.KoPercent,
            "color" : "#FF6347"
        },
        {
            "label" : "PASS",
            "data" : data.OkPercent,
            "color" : "#9ACD32"
        }];
    $.plot($("#flot-requests-summary"), dataset, {
        series : {
            pie : {
                show : true,
                radius : 1,
                label : {
                    show : true,
                    radius : 3 / 4,
                    formatter : function(label, series) {
                        return '<div style="font-size:8pt;text-align:center;padding:2px;color:white;">'
                            + label
                            + '<br/>'
                            + Math.round10(series.percent, -2)
                            + '%</div>';
                    },
                    background : {
                        opacity : 0.5,
                        color : '#000'
                    }
                }
            }
        },
        legend : {
            show : true
        }
    });

    // Creates APDEX table
    createTable($("#apdexTable"), {"supportsControllersDiscrimination": true, "overall": {"data": [0.9479392624728851, 500, 1500, "Total"], "isController": false}, "titles": ["Apdex", "T (Toleration threshold)", "F (Frustration threshold)", "Label"], "items": [{"data": [1.0, 500, 1500, "Login-0"], "isController": false}, {"data": [1.0, 500, 1500, "Login-1"], "isController": false}, {"data": [1.0, 500, 1500, "Login-2"], "isController": false}, {"data": [0.9807692307692307, 500, 1500, "Submit câu 1"], "isController": false}, {"data": [1.0, 500, 1500, "View bài 1"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 1-1"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 1-0"], "isController": false}, {"data": [1.0, 500, 1500, "View bài 3"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 3"], "isController": false}, {"data": [1.0, 500, 1500, "View bài 2"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 2"], "isController": false}, {"data": [1.0, 500, 1500, "Get bộ câu hỏi easy 1"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 3-1"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 3-0"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz 1-1"], "isController": false}, {"data": [0.5, 500, 1500, "Start Quiz medium bài 2"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz 1-0"], "isController": false}, {"data": [1.0, 500, 1500, "Login"], "isController": false}, {"data": [1.0, 500, 1500, "View Section 1"], "isController": false}, {"data": [1.0, 500, 1500, "Set grade"], "isController": false}, {"data": [0.9905660377358491, 500, 1500, "View Chủ đề 1"], "isController": false}, {"data": [0.8, 500, 1500, "View Chủ đề 2"], "isController": false}, {"data": [1.0, 500, 1500, "Get login page"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz hard bài 2"], "isController": false}, {"data": [1.0, 500, 1500, "View Bài 1"], "isController": false}, {"data": [1.0, 500, 1500, "View Grade"], "isController": false}, {"data": [1.0, 500, 1500, "Submit Quiz"], "isController": false}, {"data": [0.5, 500, 1500, "Start Quiz 1"], "isController": false}, {"data": [1.0, 500, 1500, "test login"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 2-0"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz easy bài 2-1"], "isController": false}, {"data": [1.0, 500, 1500, "View video bai 1"], "isController": false}, {"data": [1.0, 500, 1500, "View video bai 3"], "isController": false}, {"data": [1.0, 500, 1500, "Get bộ câu hỏi medium bài 2"], "isController": false}, {"data": [1.0, 500, 1500, "View video bai 2"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz hard bài 2-0"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 2-1"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz hard bài 2-1"], "isController": false}, {"data": [0.6851851851851852, 500, 1500, "View pdf bai 1"], "isController": false}, {"data": [0.5508474576271186, 500, 1500, "View pdf bai 2"], "isController": false}, {"data": [1.0, 500, 1500, "Debug Sampler"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz medium bài 2-1"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz medium bài 2-0"], "isController": false}, {"data": [1.0, 500, 1500, "test login-0"], "isController": false}, {"data": [1.0, 500, 1500, "Submit Quiz-1"], "isController": false}, {"data": [1.0, 500, 1500, "test login-1"], "isController": false}, {"data": [1.0, 500, 1500, "Submit Quiz-0"], "isController": false}, {"data": [0.5, 500, 1500, "Start Quiz easy bài 2"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz easy bài 2-0"], "isController": false}]}, function(index, item){
        switch(index){
            case 0:
                item = item.toFixed(3);
                break;
            case 1:
            case 2:
                item = formatDuration(item);
                break;
        }
        return item;
    }, [[0, 0]], 3);

    // Create statistics table
    createTable($("#statisticsTable"), {"supportsControllersDiscrimination": true, "overall": {"data": ["Total", 922, 0, 0.0, 291.7744034707154, 0, 6388, 277.5, 501.70000000000005, 557.6999999999998, 613.31, 1.1352568672574435, 775.3482402075631, 0.46292600798681527], "isController": false}, "titles": ["Label", "#Samples", "FAIL", "Error %", "Average", "Min", "Max", "Median", "90th pct", "95th pct", "99th pct", "Transactions/s", "Received", "Sent"], "items": [{"data": ["Login-0", 20, 0, 0.0, 118.69999999999999, 85, 156, 118.5, 126.9, 154.54999999999998, 156.0, 0.4203093476798924, 0.945039298924008, 0.14201858818090113], "isController": false}, {"data": ["Login-1", 20, 0, 0.0, 43.550000000000004, 41, 49, 43.0, 46.0, 48.849999999999994, 49.0, 0.4206983592763988, 0.7752517616743795, 0.14482048012200252], "isController": false}, {"data": ["Login-2", 20, 0, 0.0, 288.05, 277, 308, 287.5, 298.8, 307.55, 308.0, 0.41861146576804736, 86.9984184335559, 0.1330644844799799], "isController": false}, {"data": ["Submit câu 1", 26, 0, 0.0, 377.3846153846154, 348, 504, 360.0, 448.6, 499.79999999999995, 504.0, 0.04725820611484835, 7.407031549623843, 0.040784698088223804], "isController": false}, {"data": ["View bài 1", 20, 0, 0.0, 266.4, 255, 319, 261.5, 283.7, 317.25, 319.0, 0.03505905698148531, 6.667075415099235, 0.010189038435244168], "isController": false}, {"data": ["Submit câu 1-1", 26, 0, 0.0, 265.38461538461536, 241, 362, 252.5, 315.1, 352.19999999999993, 362.0, 0.047267570810457044, 7.316918410037087, 0.014788869623313822], "isController": false}, {"data": ["Submit câu 1-0", 26, 0, 0.0, 111.76923076923077, 98, 170, 109.0, 127.9, 155.99999999999994, 170.0, 0.047286913346731296, 0.09161839460929187, 0.026014551524548273], "isController": false}, {"data": ["View bài 3", 10, 0, 0.0, 267.7, 254, 286, 267.0, 284.9, 286.0, 286.0, 0.05976929053852131, 11.313206024744487, 0.017347102683641143], "isController": false}, {"data": ["Submit câu 3", 26, 0, 0.0, 349.7692307692308, 313, 391, 348.5, 372.6, 385.04999999999995, 391.0, 0.05222697844833647, 8.185880524258428, 0.04507283968627656], "isController": false}, {"data": ["View bài 2", 33, 0, 0.0, 268.6363636363637, 252, 338, 263.0, 303.6000000000001, 327.49999999999994, 338.0, 0.06580692248941605, 12.498366900887795, 0.019160579734060268], "isController": false}, {"data": ["Submit câu 2", 26, 0, 0.0, 357.2692307692307, 302, 393, 357.0, 376.4, 389.15, 393.0, 0.04955873663343689, 7.76766929788613, 0.042770098092941695], "isController": false}, {"data": ["Get bộ câu hỏi easy 1", 7, 0, 0.0, 283.0, 275, 304, 281.0, 304.0, 304.0, 304.0, 0.022901562540895648, 3.5442851808896276, 0.009287784919975397], "isController": false}, {"data": ["Submit câu 3-1", 26, 0, 0.0, 246.50000000000003, 234, 285, 246.0, 256.3, 277.65, 285.0, 0.05223820622036487, 8.086430764913002, 0.016344060164349434], "isController": false}, {"data": ["Submit câu 3-0", 26, 0, 0.0, 103.11538461538461, 67, 125, 103.5, 112.5, 121.85, 125.0, 0.05225279904176406, 0.10123783552326153, 0.02874649742956423], "isController": false}, {"data": ["Start Quiz 1-1", 7, 0, 0.0, 264.8571428571429, 239, 342, 253.0, 342.0, 342.0, 342.0, 0.021567793737945144, 3.3378688285298774, 0.006598517252694434], "isController": false}, {"data": ["Start Quiz medium bài 2", 6, 0, 0.0, 584.3333333333334, 565, 625, 581.0, 625.0, 625.0, 625.0, 0.03566333808844508, 5.575740014265335, 0.022428896219686162], "isController": false}, {"data": ["Start Quiz 1-0", 7, 0, 0.0, 332.4285714285714, 314, 358, 328.0, 358.0, 358.0, 358.0, 0.02156447160883281, 0.04140210076461455, 0.006976563847779476], "isController": false}, {"data": ["Login", 20, 0, 0.0, 451.95, 416, 493, 449.5, 478.50000000000006, 492.34999999999997, 493.0, 0.4174058228112282, 88.4555495408536, 0.41740582281122823], "isController": false}, {"data": ["View Section 1", 7, 0, 0.0, 317.5714285714286, 303, 337, 311.0, 337.0, 337.0, 337.0, 0.08162694155510984, 25.664578589982042, 0.024176059838378654], "isController": false}, {"data": ["Set grade", 20, 0, 0.0, 260.95, 223, 296, 262.5, 283.9, 295.4, 296.0, 0.07522926117342602, 11.70539754080247, 0.03368419555470296], "isController": false}, {"data": ["View Chủ đề 1", 53, 0, 0.0, 313.18867924528297, 281, 1026, 298.0, 310.0, 329.49999999999994, 1026.0, 0.08445299951559034, 21.88808965472666, 0.025067315912379217], "isController": false}, {"data": ["View Chủ đề 2", 10, 0, 0.0, 429.40000000000003, 287, 781, 318.0, 764.3000000000001, 781.0, 781.0, 0.05901968306430194, 18.55656068330038, 0.017475359282320652], "isController": false}, {"data": ["Get login page", 20, 0, 0.0, 124.50000000000003, 116, 144, 123.0, 133.8, 143.5, 144.0, 1.0542406831479625, 19.771130936692845, 0.1400163407305888], "isController": false}, {"data": ["Start Quiz hard bài 2", 6, 0, 0.0, 377.8333333333333, 363, 398, 377.5, 398.0, 398.0, 398.0, 0.036074168490416295, 5.639230977640027, 0.02268727002717587], "isController": false}, {"data": ["View Bài 1", 7, 0, 0.0, 266.0, 255, 280, 263.0, 280.0, 280.0, 280.0, 0.1166880594775709, 22.19021729504576, 0.033974327585057265], "isController": false}, {"data": ["View Grade", 7, 0, 0.0, 298.7142857142857, 289, 306, 300.0, 306.0, 306.0, 306.0, 0.1128140663024384, 26.99186706272462, 0.03449894438266531], "isController": false}, {"data": ["Submit Quiz", 26, 0, 0.0, 364.34615384615387, 342, 398, 365.5, 389.4, 396.95, 398.0, 0.054960502423546775, 8.85739567875692, 0.0362164608818624], "isController": false}, {"data": ["Start Quiz 1", 7, 0, 0.0, 597.5714285714286, 563, 662, 592.0, 662.0, 662.0, 662.0, 0.021546947720948558, 3.3760111193793247, 0.01356303405648994], "isController": false}, {"data": ["test login", 20, 0, 0.0, 349.15000000000003, 304, 376, 352.5, 363.7, 375.4, 376.0, 0.2787650707366367, 58.11624231218203, 0.15027179594396822], "isController": false}, {"data": ["Submit câu 2-0", 26, 0, 0.0, 104.99999999999999, 66, 115, 105.0, 112.3, 114.3, 115.0, 0.04958104021022361, 0.09606140313867054, 0.02727664873644626], "isController": false}, {"data": ["Start Quiz easy bài 2-1", 7, 0, 0.0, 254.00000000000003, 244, 278, 250.0, 278.0, 278.0, 278.0, 0.07082726242512548, 10.935490197380403, 0.021728397052574067], "isController": false}, {"data": ["View video bai 1", 60, 0, 0.0, 283.1500000000001, 258, 382, 276.5, 309.5, 337.4, 382.0, 0.0930487901331063, 14.435465720825716, 0.026860568714205293], "isController": false}, {"data": ["View video bai 3", 20, 0, 0.0, 274.84999999999997, 259, 299, 274.5, 294.3, 298.8, 299.0, 0.10166476045240817, 15.768859607319863, 0.0293080442241708], "isController": false}, {"data": ["Get bộ câu hỏi medium bài 2", 6, 0, 0.0, 291.5, 282, 304, 291.0, 304.0, 304.0, 304.0, 0.03586500412447548, 5.538411232620416, 0.014535133507477852], "isController": false}, {"data": ["View video bai 2", 6, 0, 0.0, 284.6666666666667, 268, 299, 283.5, 299.0, 299.0, 299.0, 0.03581405343456772, 5.556984076176492, 0.010317525159372537], "isController": false}, {"data": ["Start Quiz hard bài 2-0", 6, 0, 0.0, 128.0, 121, 142, 126.0, 142.0, 142.0, 142.0, 0.036128255306337495, 0.06936342766822219, 0.011678176275779016], "isController": false}, {"data": ["Submit câu 2-1", 26, 0, 0.0, 251.9230769230769, 236, 278, 250.5, 271.7, 278.0, 278.0, 0.049569129871120256, 7.673259971616907, 0.0155089712975673], "isController": false}, {"data": ["Start Quiz hard bài 2-1", 6, 0, 0.0, 249.5, 239, 256, 251.0, 256.0, 256.0, 256.0, 0.036104993320576234, 5.574730848557606, 0.011035998934902699], "isController": false}, {"data": ["View pdf bai 1", 27, 0, 0.0, 509.4814814814815, 434, 592, 510.0, 554.0, 588.0, 592.0, 0.0406510797378457, 223.67601603468668, 0.01312985178164649], "isController": false}, {"data": ["View pdf bai 2", 59, 0, 0.0, 683.0847457627117, 468, 6388, 546.0, 593.0, 757.0, 6388.0, 0.11219694938396269, 704.4627317152251, 0.03628350101072337], "isController": false}, {"data": ["Debug Sampler", 20, 0, 0.0, 0.7500000000000001, 0, 6, 0.0, 1.9000000000000021, 5.799999999999997, 6.0, 0.08342440497543152, 0.07120810661013273, 0.0], "isController": false}, {"data": ["Start Quiz medium bài 2-1", 6, 0, 0.0, 249.33333333333331, 241, 257, 251.0, 257.0, 257.0, 257.0, 0.035735131207490084, 5.518355759609773, 0.01092294537885195], "isController": false}, {"data": ["Start Quiz medium bài 2-0", 6, 0, 0.0, 335.0, 315, 368, 332.0, 368.0, 368.0, 368.0, 0.03571704953359486, 0.06857394471000733, 0.011545257222285058], "isController": false}, {"data": ["test login-0", 20, 0, 0.0, 64.0, 32, 83, 65.0, 67.0, 82.19999999999999, 83.0, 0.27987293768629046, 0.1336365946110466, 0.07529784602790333], "isController": false}, {"data": ["Submit Quiz-1", 26, 0, 0.0, 257.42307692307696, 240, 290, 258.5, 273.5, 285.45, 290.0, 0.05497665606603965, 8.754559609893048, 0.01677134918000203], "isController": false}, {"data": ["test login-1", 20, 0, 0.0, 284.5999999999999, 269, 298, 286.0, 295.9, 297.9, 298.0, 0.2788933511825078, 58.00981704596162, 0.0753066519550424], "isController": false}, {"data": ["Submit Quiz-0", 26, 0, 0.0, 106.61538461538461, 71, 138, 108.0, 117.9, 131.7, 138.0, 0.054992121321079966, 0.10546903917131104, 0.019461229232542645], "isController": false}, {"data": ["Start Quiz easy bài 2", 7, 0, 0.0, 582.5714285714286, 558, 611, 580.0, 611.0, 611.0, 611.0, 0.07058443915621344, 11.03351571323055, 0.04454854948977534], "isController": false}, {"data": ["Start Quiz easy bài 2-0", 7, 0, 0.0, 328.2857142857143, 313, 346, 331.0, 346.0, 346.0, 346.0, 0.07075853145722141, 0.13585085238759503, 0.02295111406780689], "isController": false}]}, function(index, item){
        switch(index){
            // Errors pct
            case 3:
                item = item.toFixed(2) + '%';
                break;
            // Mean
            case 4:
            // Mean
            case 7:
            // Median
            case 8:
            // Percentile 1
            case 9:
            // Percentile 2
            case 10:
            // Percentile 3
            case 11:
            // Throughput
            case 12:
            // Kbytes/s
            case 13:
            // Sent Kbytes/s
                item = item.toFixed(2);
                break;
        }
        return item;
    }, [[0, 0]], 0, summaryTableHeader);

    // Create error table
    createTable($("#errorsTable"), {"supportsControllersDiscrimination": false, "titles": ["Type of error", "Number of errors", "% in errors", "% in all samples"], "items": []}, function(index, item){
        switch(index){
            case 2:
            case 3:
                item = item.toFixed(2) + '%';
                break;
        }
        return item;
    }, [[1, 1]]);

        // Create top5 errors by sampler
    createTable($("#top5ErrorsBySamplerTable"), {"supportsControllersDiscrimination": false, "overall": {"data": ["Total", 922, 0, "", "", "", "", "", "", "", "", "", ""], "isController": false}, "titles": ["Sample", "#Samples", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors"], "items": [{"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}]}, function(index, item){
        return item;
    }, [[0, 0]], 0);

});
