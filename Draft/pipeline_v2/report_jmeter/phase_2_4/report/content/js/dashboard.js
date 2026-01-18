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

    var data = {"OkPercent": 99.89082969432314, "KoPercent": 0.1091703056768559};
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
    createTable($("#apdexTable"), {"supportsControllersDiscrimination": true, "overall": {"data": [0.9563318777292577, 500, 1500, "Total"], "isController": false}, "titles": ["Apdex", "T (Toleration threshold)", "F (Frustration threshold)", "Label"], "items": [{"data": [1.0, 500, 1500, "Login-0"], "isController": false}, {"data": [1.0, 500, 1500, "Login-1"], "isController": false}, {"data": [1.0, 500, 1500, "Login-2"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 1"], "isController": false}, {"data": [1.0, 500, 1500, "View bài 1"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 1-1"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 1-0"], "isController": false}, {"data": [1.0, 500, 1500, "View bài 3"], "isController": false}, {"data": [0.9615384615384616, 500, 1500, "Submit câu 3"], "isController": false}, {"data": [1.0, 500, 1500, "View bài 2"], "isController": false}, {"data": [0.9807692307692307, 500, 1500, "Submit câu 2"], "isController": false}, {"data": [1.0, 500, 1500, "Get bộ câu hỏi easy 1"], "isController": false}, {"data": [0.9615384615384616, 500, 1500, "Submit câu 3-1"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 3-0"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz 1-1"], "isController": false}, {"data": [0.5833333333333334, 500, 1500, "Start Quiz medium bài 2"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz 1-0"], "isController": false}, {"data": [1.0, 500, 1500, "Login"], "isController": false}, {"data": [1.0, 500, 1500, "View Section 1"], "isController": false}, {"data": [0.95, 500, 1500, "Set grade"], "isController": false}, {"data": [1.0, 500, 1500, "View Chủ đề 1"], "isController": false}, {"data": [1.0, 500, 1500, "View Chủ đề 2"], "isController": false}, {"data": [1.0, 500, 1500, "Get login page"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz hard bài 2"], "isController": false}, {"data": [1.0, 500, 1500, "View Bài 1"], "isController": false}, {"data": [1.0, 500, 1500, "View Grade"], "isController": false}, {"data": [1.0, 500, 1500, "Submit Quiz"], "isController": false}, {"data": [0.5, 500, 1500, "Start Quiz 1"], "isController": false}, {"data": [1.0, 500, 1500, "test login"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 2-0"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz easy bài 2-1"], "isController": false}, {"data": [0.9933333333333333, 500, 1500, "View video bai 1"], "isController": false}, {"data": [1.0, 500, 1500, "View video bai 3"], "isController": false}, {"data": [1.0, 500, 1500, "Get bộ câu hỏi medium bài 2"], "isController": false}, {"data": [1.0, 500, 1500, "View video bai 2"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz hard bài 2-0"], "isController": false}, {"data": [0.9807692307692307, 500, 1500, "Submit câu 2-1"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz hard bài 2-1"], "isController": false}, {"data": [0.7741935483870968, 500, 1500, "View pdf bai 1"], "isController": false}, {"data": [0.6041666666666666, 500, 1500, "View pdf bai 2"], "isController": false}, {"data": [1.0, 500, 1500, "Debug Sampler"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz medium bài 2-1"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz medium bài 2-0"], "isController": false}, {"data": [1.0, 500, 1500, "test login-0"], "isController": false}, {"data": [1.0, 500, 1500, "Submit Quiz-1"], "isController": false}, {"data": [1.0, 500, 1500, "test login-1"], "isController": false}, {"data": [1.0, 500, 1500, "Submit Quiz-0"], "isController": false}, {"data": [0.5, 500, 1500, "Start Quiz easy bài 2"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz easy bài 2-0"], "isController": false}]}, function(index, item){
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
    createTable($("#statisticsTable"), {"supportsControllersDiscrimination": true, "overall": {"data": ["Total", 916, 1, 0.1091703056768559, 283.0229257641919, 0, 1231, 274.0, 477.60000000000014, 553.15, 621.3200000000002, 1.1433935320874173, 726.45355638609, 0.46481324598314366], "isController": false}, "titles": ["Label", "#Samples", "FAIL", "Error %", "Average", "Min", "Max", "Median", "90th pct", "95th pct", "99th pct", "Transactions/s", "Received", "Sent"], "items": [{"data": ["Login-0", 20, 0, 0.0, 119.60000000000002, 87, 132, 120.5, 131.0, 131.95, 132.0, 0.4195510803440319, 0.9431704950702747, 0.14176237675687015], "isController": false}, {"data": ["Login-1", 20, 0, 0.0, 43.75, 41, 51, 43.0, 47.900000000000006, 50.849999999999994, 51.0, 0.4200445247196203, 0.7740468927206284, 0.14434928539925232], "isController": false}, {"data": ["Login-2", 20, 0, 0.0, 290.55, 277, 320, 288.0, 313.6, 319.75, 320.0, 0.41796409688407765, 86.86502110718689, 0.13253217017408206], "isController": false}, {"data": ["Submit câu 1", 26, 0, 0.0, 364.6538461538462, 342, 441, 360.0, 398.1, 430.15, 441.0, 0.04822852902986459, 7.560247620455388, 0.041442769198664436], "isController": false}, {"data": ["View bài 1", 25, 0, 0.0, 273.28, 255, 425, 263.0, 293.8, 387.7999999999999, 425.0, 0.046420945130442856, 8.827943668183085, 0.01343487431529106], "isController": false}, {"data": ["Submit câu 1-1", 26, 0, 0.0, 251.7307692307692, 239, 282, 250.5, 262.9, 276.04999999999995, 282.0, 0.04823828227187467, 7.468314855326898, 0.01505996853379741], "isController": false}, {"data": ["Submit câu 1-0", 26, 0, 0.0, 112.61538461538461, 100, 181, 108.0, 131.40000000000003, 175.39999999999998, 181.0, 0.0482519792590723, 0.09348820981445259, 0.02639867525118867], "isController": false}, {"data": ["View bài 3", 7, 0, 0.0, 263.1428571428571, 255, 283, 262.0, 283.0, 283.0, 283.0, 0.0586323583609743, 11.098006081013168, 0.0169729553012028], "isController": false}, {"data": ["Submit câu 3", 26, 0, 0.0, 415.8846153846155, 306, 1175, 351.0, 643.5000000000005, 1139.6499999999999, 1175.0, 0.05290865321023253, 8.293940127754048, 0.04546439934433969], "isController": false}, {"data": ["View bài 2", 27, 0, 0.0, 264.88888888888886, 250, 289, 263.0, 277.4, 285.0, 289.0, 0.058671673316122976, 11.143316444176076, 0.017000100366589308], "isController": false}, {"data": ["Submit câu 2", 26, 0, 0.0, 393.7692307692308, 340, 1231, 359.0, 385.3, 935.2499999999987, 1231.0, 0.05068008779350593, 7.9445929737175005, 0.043549393349602936], "isController": false}, {"data": ["Get bộ câu hỏi easy 1", 8, 0, 0.0, 289.625, 273, 311, 289.5, 311.0, 311.0, 311.0, 0.02730524533762936, 4.225963357854013, 0.011059424320099391], "isController": false}, {"data": ["Submit câu 3-1", 26, 0, 0.0, 298.6923076923076, 234, 923, 246.5, 447.3000000000004, 886.5999999999999, 923.0, 0.05292071459247996, 8.193298968580361, 0.016521821653121], "isController": false}, {"data": ["Submit câu 3-0", 26, 0, 0.0, 116.9230769230769, 72, 355, 103.0, 156.3, 290.59999999999974, 355.0, 0.05293439799337913, 0.10255840789109359, 0.028960428229100076], "isController": false}, {"data": ["Start Quiz 1-1", 8, 0, 0.0, 247.125, 237, 261, 246.0, 261.0, 261.0, 261.0, 0.025696041524803103, 3.9769109774693896, 0.00784808299500212], "isController": false}, {"data": ["Start Quiz medium bài 2", 6, 0, 0.0, 548.5, 376, 618, 574.5, 618.0, 618.0, 618.0, 0.0712064750421305, 11.13268733236809, 0.044735838812275996], "isController": false}, {"data": ["Start Quiz 1-0", 8, 0, 0.0, 333.75, 314, 354, 334.0, 354.0, 354.0, 354.0, 0.02568795555983688, 0.0493188678033587, 0.00829715947403911], "isController": false}, {"data": ["Login", 20, 0, 0.0, 455.09999999999997, 419, 494, 454.5, 484.40000000000003, 493.55, 494.0, 0.4166927099610392, 88.30540515553055, 0.4161230128966394], "isController": false}, {"data": ["View Section 1", 8, 0, 0.0, 312.5, 299, 344, 307.5, 344.0, 344.0, 344.0, 0.10417480532333255, 32.75441796803787, 0.030799728819959894], "isController": false}, {"data": ["Set grade", 20, 1, 5.0, 254.2, 19, 348, 261.0, 302.6, 345.75, 348.0, 0.07679282447848074, 11.359376079899095, 0.03262945110408884], "isController": false}, {"data": ["View Chủ đề 1", 52, 0, 0.0, 302.94230769230774, 280, 441, 299.5, 322.1, 326.09999999999997, 441.0, 0.08778979072264505, 22.753180493804912, 0.025937293187512242], "isController": false}, {"data": ["View Chủ đề 2", 7, 0, 0.0, 311.1428571428571, 296, 322, 315.0, 322.0, 322.0, 322.0, 0.056986551173922956, 17.91731741152838, 0.016830430920088575], "isController": false}, {"data": ["Get login page", 20, 0, 0.0, 124.95, 116, 153, 122.5, 130.9, 151.89999999999998, 153.0, 1.0557432432432432, 19.79930980785473, 0.14021589949324326], "isController": false}, {"data": ["Start Quiz hard bài 2", 6, 0, 0.0, 383.6666666666667, 358, 448, 371.0, 448.0, 448.0, 448.0, 0.07194589668569236, 11.246839251882584, 0.045200384310998126], "isController": false}, {"data": ["View Bài 1", 6, 0, 0.0, 270.5, 258, 302, 266.0, 302.0, 302.0, 302.0, 0.15770383220312253, 29.990397109748727, 0.04568893576197235], "isController": false}, {"data": ["View Grade", 6, 0, 0.0, 303.33333333333337, 285, 331, 300.0, 331.0, 331.0, 331.0, 0.15552099533437014, 37.225332304626754, 0.04735999060393987], "isController": false}, {"data": ["Submit Quiz", 26, 0, 0.0, 363.6153846153846, 317, 442, 361.5, 378.6, 420.2999999999999, 442.0, 0.05577508055208749, 8.996771464154858, 0.03667781363829431], "isController": false}, {"data": ["Start Quiz 1", 8, 0, 0.0, 581.25, 551, 603, 580.0, 603.0, 603.0, 603.0, 0.025667845248560996, 4.02182736910201, 0.016130135173290042], "isController": false}, {"data": ["test login", 20, 0, 0.0, 349.84999999999997, 306, 379, 349.0, 371.20000000000005, 378.65, 379.0, 0.2787456445993031, 58.11295459494774, 0.14982578397212543], "isController": false}, {"data": ["Submit câu 2-0", 26, 0, 0.0, 120.88461538461537, 98, 450, 106.5, 124.6, 336.59999999999957, 450.0, 0.05070548886917009, 0.09824188468401705, 0.027740991243552116], "isController": false}, {"data": ["Start Quiz easy bài 2-1", 6, 0, 0.0, 250.5, 245, 263, 245.5, 263.0, 263.0, 263.0, 0.06759877871539788, 10.434868312649984, 0.020640512511407295], "isController": false}, {"data": ["View video bai 1", 75, 0, 0.0, 289.2, 255, 900, 274.0, 300.4, 380.6000000000001, 900.0, 0.12226094724521633, 18.96795974853776, 0.03514524651474793], "isController": false}, {"data": ["View video bai 3", 14, 0, 0.0, 269.64285714285717, 260, 278, 272.0, 276.5, 278.0, 278.0, 0.09363859515353386, 14.523949638320927, 0.026923708790657544], "isController": false}, {"data": ["Get bộ câu hỏi medium bài 2", 6, 0, 0.0, 282.3333333333333, 270, 309, 279.0, 309.0, 309.0, 309.0, 0.07092450086882514, 10.952432932018867, 0.02872072886745393], "isController": false}, {"data": ["View video bai 2", 6, 0, 0.0, 271.8333333333333, 262, 292, 270.5, 292.0, 292.0, 292.0, 0.07063560269828002, 10.95996911163957, 0.020326130463958186], "isController": false}, {"data": ["Start Quiz hard bài 2-0", 6, 0, 0.0, 127.83333333333333, 120, 144, 125.0, 144.0, 144.0, 144.0, 0.07220911760458287, 0.13863586446348625, 0.023317527559813218], "isController": false}, {"data": ["Submit câu 2-1", 26, 0, 0.0, 272.69230769230774, 236, 781, 253.0, 276.6, 604.9499999999994, 781.0, 0.050691055563245865, 7.848098357341723, 0.01582572317614557], "isController": false}, {"data": ["Start Quiz hard bài 2-1", 6, 0, 0.0, 255.33333333333331, 233, 304, 243.0, 304.0, 304.0, 304.0, 0.07205476161883032, 11.125517893599136, 0.022001095832832954], "isController": false}, {"data": ["View pdf bai 1", 31, 0, 0.0, 493.77419354838713, 439, 622, 491.0, 548.6, 578.8, 622.0, 0.050539385669312646, 278.08482609203793, 0.016258449044071973], "isController": false}, {"data": ["View pdf bai 2", 48, 0, 0.0, 540.0624999999999, 463, 718, 544.0, 591.2, 601.6999999999999, 718.0, 0.10264305876315113, 644.4757185014114, 0.03304909358694723], "isController": false}, {"data": ["Debug Sampler", 20, 0, 0.0, 0.7000000000000001, 0, 3, 1.0, 1.9000000000000021, 2.9499999999999993, 3.0, 0.0848392296597947, 0.07289628536735386, 0.0], "isController": false}, {"data": ["Start Quiz medium bài 2-1", 6, 0, 0.0, 245.5, 241, 259, 243.0, 259.0, 259.0, 259.0, 0.07148984844152131, 11.039736068415785, 0.021828606067105138], "isController": false}, {"data": ["Start Quiz medium bài 2-0", 6, 0, 0.0, 302.5, 134, 373, 331.0, 373.0, 373.0, 373.0, 0.07141156867412521, 0.13710463282551774, 0.023059985717686266], "isController": false}, {"data": ["test login-0", 20, 0, 0.0, 63.1, 32, 75, 64.0, 66.0, 74.55, 75.0, 0.2798376941374003, 0.13361976616062685, 0.07506974080033581], "isController": false}, {"data": ["Submit Quiz-1", 26, 0, 0.0, 256.2307692307693, 241, 340, 251.5, 265.9, 314.7999999999999, 340.0, 0.05578740706568967, 8.891763378249347, 0.016980962547338833], "isController": false}, {"data": ["test login-1", 20, 0, 0.0, 286.5, 272, 314, 284.0, 307.20000000000005, 313.7, 314.0, 0.2788700186842913, 58.00572642153992, 0.07508248452271396], "isController": false}, {"data": ["Submit Quiz-0", 26, 0, 0.0, 107.03846153846155, 69, 126, 106.5, 115.6, 122.85, 126.0, 0.05580476916142603, 0.10702970732008327, 0.019711089588117875], "isController": false}, {"data": ["Start Quiz easy bài 2", 6, 0, 0.0, 585.6666666666666, 563, 614, 588.0, 614.0, 614.0, 614.0, 0.06735669862367813, 10.526819279872695, 0.042317196726464446], "isController": false}, {"data": ["Start Quiz easy bài 2-0", 6, 0, 0.0, 334.8333333333333, 318, 351, 335.5, 351.0, 351.0, 351.0, 0.06754322766570606, 0.12967772030349425, 0.02181083393371758], "isController": false}]}, function(index, item){
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
    createTable($("#errorsTable"), {"supportsControllersDiscrimination": false, "titles": ["Type of error", "Number of errors", "% in errors", "% in all samples"], "items": [{"data": ["Non HTTP response code: org.apache.http.NoHttpResponseException/Non HTTP response message: 139.99.103.223:9090 failed to respond", 1, 100.0, 0.1091703056768559], "isController": false}]}, function(index, item){
        switch(index){
            case 2:
            case 3:
                item = item.toFixed(2) + '%';
                break;
        }
        return item;
    }, [[1, 1]]);

        // Create top5 errors by sampler
    createTable($("#top5ErrorsBySamplerTable"), {"supportsControllersDiscrimination": false, "overall": {"data": ["Total", 916, 1, "Non HTTP response code: org.apache.http.NoHttpResponseException/Non HTTP response message: 139.99.103.223:9090 failed to respond", 1, "", "", "", "", "", "", "", ""], "isController": false}, "titles": ["Sample", "#Samples", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors"], "items": [{"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": ["Set grade", 20, 1, "Non HTTP response code: org.apache.http.NoHttpResponseException/Non HTTP response message: 139.99.103.223:9090 failed to respond", 1, "", "", "", "", "", "", "", ""], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}]}, function(index, item){
        return item;
    }, [[0, 0]], 0);

});
