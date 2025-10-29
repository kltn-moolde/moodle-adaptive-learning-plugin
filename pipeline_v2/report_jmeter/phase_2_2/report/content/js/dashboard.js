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
    createTable($("#apdexTable"), {"supportsControllersDiscrimination": true, "overall": {"data": [0.9545454545454546, 500, 1500, "Total"], "isController": false}, "titles": ["Apdex", "T (Toleration threshold)", "F (Frustration threshold)", "Label"], "items": [{"data": [1.0, 500, 1500, "Login-0"], "isController": false}, {"data": [1.0, 500, 1500, "Login-1"], "isController": false}, {"data": [1.0, 500, 1500, "Login-2"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 1"], "isController": false}, {"data": [1.0, 500, 1500, "View bài 1"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 1-1"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 1-0"], "isController": false}, {"data": [1.0, 500, 1500, "View bài 3"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 3"], "isController": false}, {"data": [1.0, 500, 1500, "View bài 2"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 2"], "isController": false}, {"data": [1.0, 500, 1500, "Get bộ câu hỏi easy 1"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 3-1"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 3-0"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz 1-1"], "isController": false}, {"data": [0.5, 500, 1500, "Start Quiz medium bài 2"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz 1-0"], "isController": false}, {"data": [0.95, 500, 1500, "Login"], "isController": false}, {"data": [1.0, 500, 1500, "View Section 1"], "isController": false}, {"data": [1.0, 500, 1500, "Set grade"], "isController": false}, {"data": [1.0, 500, 1500, "View Chủ đề 1"], "isController": false}, {"data": [1.0, 500, 1500, "View Chủ đề 2"], "isController": false}, {"data": [1.0, 500, 1500, "Get login page"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz hard bài 2"], "isController": false}, {"data": [1.0, 500, 1500, "View Bài 1"], "isController": false}, {"data": [1.0, 500, 1500, "View Grade"], "isController": false}, {"data": [1.0, 500, 1500, "Submit Quiz"], "isController": false}, {"data": [0.5, 500, 1500, "Start Quiz 1"], "isController": false}, {"data": [1.0, 500, 1500, "test login"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 2-0"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz easy bài 2-1"], "isController": false}, {"data": [1.0, 500, 1500, "View video bai 1"], "isController": false}, {"data": [1.0, 500, 1500, "View video bai 3"], "isController": false}, {"data": [1.0, 500, 1500, "Get bộ câu hỏi medium bài 2"], "isController": false}, {"data": [1.0, 500, 1500, "View video bai 2"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz hard bài 2-0"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 2-1"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz hard bài 2-1"], "isController": false}, {"data": [0.6935483870967742, 500, 1500, "View pdf bai 1"], "isController": false}, {"data": [0.5877192982456141, 500, 1500, "View pdf bai 2"], "isController": false}, {"data": [1.0, 500, 1500, "Debug Sampler"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz medium bài 2-1"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz medium bài 2-0"], "isController": false}, {"data": [1.0, 500, 1500, "test login-0"], "isController": false}, {"data": [1.0, 500, 1500, "Submit Quiz-1"], "isController": false}, {"data": [1.0, 500, 1500, "test login-1"], "isController": false}, {"data": [1.0, 500, 1500, "Submit Quiz-0"], "isController": false}, {"data": [0.6428571428571429, 500, 1500, "Start Quiz easy bài 2"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz easy bài 2-0"], "isController": false}]}, function(index, item){
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
    createTable($("#statisticsTable"), {"supportsControllersDiscrimination": true, "overall": {"data": ["Total", 946, 0, 0.0, 281.4196617336152, 0, 954, 274.5, 489.50000000000034, 550.0, 607.8299999999997, 1.1124176857949202, 756.3223866617915, 0.4488432373735889], "isController": false}, "titles": ["Label", "#Samples", "FAIL", "Error %", "Average", "Min", "Max", "Median", "90th pct", "95th pct", "99th pct", "Transactions/s", "Received", "Sent"], "items": [{"data": ["Login-0", 20, 0, 0.0, 122.74999999999999, 95, 159, 122.5, 133.0, 157.7, 159.0, 0.42003570303475796, 0.9438907775910952, 0.14192612622072875], "isController": false}, {"data": ["Login-1", 20, 0, 0.0, 58.45000000000001, 42, 332, 43.5, 52.40000000000001, 318.0499999999998, 332.0, 0.42053913116615504, 0.7749583403423188, 0.14423178014214222], "isController": false}, {"data": ["Login-2", 20, 0, 0.0, 294.75, 272, 338, 290.0, 320.40000000000003, 337.2, 338.0, 0.4184713242525056, 86.96929335886009, 0.13248867511978743], "isController": false}, {"data": ["Submit câu 1", 26, 0, 0.0, 364.0, 343, 389, 363.5, 385.5, 389.0, 389.0, 0.0440729509044278, 6.907633848280561, 0.03796954908709663], "isController": false}, {"data": ["View bài 1", 24, 0, 0.0, 263.25, 253, 277, 263.0, 273.0, 276.5, 277.0, 0.04050646584461045, 7.70299277381527, 0.011679232461544174], "isController": false}, {"data": ["Submit câu 1-1", 26, 0, 0.0, 254.6538461538462, 239, 275, 253.0, 272.3, 274.3, 275.0, 0.04408146933709947, 6.82356111090389, 0.013758902125574542], "isController": false}, {"data": ["Submit câu 1-0", 26, 0, 0.0, 109.07692307692308, 101, 129, 108.5, 115.3, 124.44999999999999, 129.0, 0.04409103781823979, 0.08542638577283959, 0.02422324256938827], "isController": false}, {"data": ["View bài 3", 11, 0, 0.0, 267.8181818181818, 253, 294, 265.0, 292.0, 294.0, 294.0, 0.06603869867742498, 12.499887434036346, 0.019212430359190485], "isController": false}, {"data": ["Submit câu 3", 26, 0, 0.0, 353.03846153846155, 317, 392, 353.5, 377.1, 388.5, 392.0, 0.04811464609827232, 7.541157540073949, 0.04145153386253276], "isController": false}, {"data": ["View bài 2", 32, 0, 0.0, 260.59375000000006, 249, 282, 260.0, 268.8, 277.45, 282.0, 0.06646381356900294, 12.623126810879295, 0.019179743075820672], "isController": false}, {"data": ["Submit câu 2", 26, 0, 0.0, 358.96153846153845, 341, 392, 356.5, 388.0, 390.6, 392.0, 0.04583282652804, 7.183522611338512, 0.03948570996370393], "isController": false}, {"data": ["Get bộ câu hỏi easy 1", 7, 0, 0.0, 282.14285714285717, 272, 299, 283.0, 299.0, 299.0, 299.0, 0.038091299403054925, 5.895074965037629, 0.015373622931506402], "isController": false}, {"data": ["Submit câu 3-1", 26, 0, 0.0, 250.57692307692312, 231, 288, 248.0, 271.0, 284.5, 288.0, 0.04812470963216063, 7.449495011573067, 0.015020896072838599], "isController": false}, {"data": ["Submit câu 3-0", 26, 0, 0.0, 102.3076923076923, 69, 113, 103.5, 109.6, 112.3, 113.0, 0.04813673795840986, 0.09326312177391284, 0.026445915944924164], "isController": false}, {"data": ["Start Quiz 1-1", 7, 0, 0.0, 247.0, 240, 251, 248.0, 251.0, 251.0, 251.0, 0.03597196242471582, 5.567082731659438, 0.010935115251598182], "isController": false}, {"data": ["Start Quiz medium bài 2", 6, 0, 0.0, 583.0, 556, 613, 583.0, 613.0, 613.0, 613.0, 0.037486176972241485, 5.8607294810038795, 0.023648506175847656], "isController": false}, {"data": ["Start Quiz 1-0", 7, 0, 0.0, 334.42857142857144, 314, 378, 322.0, 378.0, 378.0, 378.0, 0.03595828838547285, 0.06903710445882777, 0.011563037769045052], "isController": false}, {"data": ["Login", 20, 0, 0.0, 477.2000000000001, 435, 804, 458.0, 504.00000000000006, 789.0999999999998, 804.0, 0.4171881518564873, 88.4088916484147, 0.41612888506466417], "isController": false}, {"data": ["View Section 1", 7, 0, 0.0, 307.14285714285717, 297, 316, 305.0, 316.0, 316.0, 316.0, 0.08146923954284119, 25.614995013646098, 0.02397023244919811], "isController": false}, {"data": ["Set grade", 20, 0, 0.0, 265.04999999999995, 216, 342, 263.0, 298.5, 339.84999999999997, 342.0, 0.06471088793044874, 10.068821419587016, 0.028892400353321447], "isController": false}, {"data": ["View Chủ đề 1", 56, 0, 0.0, 303.2678571428572, 287, 438, 298.5, 317.3, 322.29999999999995, 438.0, 0.09012285676581254, 23.357573800159003, 0.02652576688918429], "isController": false}, {"data": ["View Chủ đề 2", 11, 0, 0.0, 303.909090909091, 288, 326, 300.0, 325.2, 326.0, 326.0, 0.06635179722890767, 20.861873324240122, 0.01969229919533366], "isController": false}, {"data": ["Get login page", 20, 0, 0.0, 127.15, 117, 152, 125.0, 136.8, 151.25, 152.0, 1.0541851149061774, 19.770088815095928, 0.1400089605734767], "isController": false}, {"data": ["Start Quiz hard bài 2", 6, 0, 0.0, 386.33333333333337, 369, 404, 388.0, 404.0, 404.0, 404.0, 0.03832665810704636, 5.991347457505317, 0.024178731579249945], "isController": false}, {"data": ["View Bài 1", 7, 0, 0.0, 261.0, 255, 273, 258.0, 273.0, 273.0, 273.0, 0.19469863432815065, 37.02525367319834, 0.056198587391872716], "isController": false}, {"data": ["View Grade", 7, 0, 0.0, 297.14285714285717, 284, 331, 294.0, 331.0, 331.0, 331.0, 0.2015838732901368, 48.273431875449965, 0.06113885889128869], "isController": false}, {"data": ["Submit Quiz", 26, 0, 0.0, 365.11538461538464, 343, 441, 362.0, 377.6, 419.2999999999999, 441.0, 0.05044302557267385, 8.129407777659754, 0.03316386416857283], "isController": false}, {"data": ["Start Quiz 1", 7, 0, 0.0, 581.7142857142858, 556, 626, 571.0, 626.0, 626.0, 626.0, 0.035912537579905396, 5.626835307026544, 0.022465376466001087], "isController": false}, {"data": ["test login", 20, 0, 0.0, 352.90000000000003, 316, 380, 350.0, 373.0, 379.65, 380.0, 0.27868349915001533, 58.09923647252877, 0.14952022893849454], "isController": false}, {"data": ["Submit câu 2-0", 26, 0, 0.0, 105.73076923076924, 100, 117, 106.0, 110.6, 115.25, 117.0, 0.04585238705763469, 0.0888389999241672, 0.025190912916617434], "isController": false}, {"data": ["Start Quiz easy bài 2-1", 7, 0, 0.0, 256.5714285714286, 238, 304, 247.0, 304.0, 304.0, 304.0, 0.05158361704322707, 7.9650127784594185, 0.01569529419242163], "isController": false}, {"data": ["View video bai 1", 72, 0, 0.0, 278.0694444444445, 260, 430, 273.0, 293.0, 302.2499999999999, 430.0, 0.10886410886410887, 16.889033264033262, 0.0311761718011718], "isController": false}, {"data": ["View video bai 3", 22, 0, 0.0, 294.27272727272725, 260, 433, 280.0, 377.69999999999993, 428.3499999999999, 433.0, 0.11303789338471419, 17.532905828516377, 0.032664980732177266], "isController": false}, {"data": ["Get bộ câu hỏi medium bài 2", 6, 0, 0.0, 283.16666666666663, 275, 299, 281.5, 299.0, 299.0, 299.0, 0.03734292631618256, 5.766637635134715, 0.015170563815949164], "isController": false}, {"data": ["View video bai 2", 6, 0, 0.0, 273.5, 261, 288, 270.5, 288.0, 288.0, 288.0, 0.03817765334690761, 5.9237252242937135, 0.011035727920590481], "isController": false}, {"data": ["Start Quiz hard bài 2-0", 6, 0, 0.0, 130.16666666666666, 125, 139, 129.0, 139.0, 139.0, 139.0, 0.03839017211593832, 0.07370613123040502, 0.012446813615714378], "isController": false}, {"data": ["Submit câu 2-1", 26, 0, 0.0, 252.92307692307696, 236, 286, 248.5, 276.8, 284.25, 286.0, 0.04584171560857522, 7.096097500811046, 0.014308317935218603], "isController": false}, {"data": ["Start Quiz hard bài 2-1", 6, 0, 0.0, 256.0, 242, 272, 256.0, 272.0, 272.0, 272.0, 0.038359001898770596, 5.9227572570436715, 0.011762428316615201], "isController": false}, {"data": ["View pdf bai 1", 31, 0, 0.0, 517.6774193548387, 434, 648, 507.0, 577.6, 633.5999999999999, 648.0, 0.047787662458783145, 262.94391251899947, 0.015322039708464429], "isController": false}, {"data": ["View pdf bai 2", 57, 0, 0.0, 549.0, 466, 954, 547.0, 593.4, 625.6999999999996, 954.0, 0.11348590883298657, 712.5558563457538, 0.03640539605586692], "isController": false}, {"data": ["Debug Sampler", 20, 0, 0.0, 0.8500000000000002, 0, 5, 1.0, 1.9000000000000021, 4.849999999999998, 5.0, 0.0701803635342831, 0.05991374394694364, 0.0], "isController": false}, {"data": ["Start Quiz medium bài 2-1", 6, 0, 0.0, 245.33333333333331, 236, 256, 244.5, 256.0, 256.0, 256.0, 0.03756503446591912, 5.800936425874795, 0.01151896564677598], "isController": false}, {"data": ["Start Quiz medium bài 2-0", 6, 0, 0.0, 337.66666666666663, 313, 377, 335.0, 377.0, 377.0, 377.0, 0.03754599384245701, 0.07208537489674852, 0.012173115191109108], "isController": false}, {"data": ["test login-0", 20, 0, 0.0, 63.49999999999999, 32, 71, 64.0, 69.7, 70.95, 71.0, 0.2798337787354312, 0.1336178965944229, 0.0749320528606008], "isController": false}, {"data": ["Submit Quiz-1", 26, 0, 0.0, 256.11538461538464, 241, 328, 252.0, 262.6, 305.5999999999999, 328.0, 0.05045359724445738, 8.034343087493328, 0.015353629990782514], "isController": false}, {"data": ["test login-1", 20, 0, 0.0, 288.9, 272, 315, 284.0, 308.9, 314.7, 315.0, 0.2788078177712103, 57.99202609641175, 0.07492960102601277], "isController": false}, {"data": ["Submit Quiz-0", 26, 0, 0.0, 108.76923076923077, 98, 123, 108.0, 117.3, 121.25, 123.0, 0.0504666221525179, 0.09679340420658705, 0.017821784160080126], "isController": false}, {"data": ["Start Quiz easy bài 2", 7, 0, 0.0, 526.4285714285714, 383, 626, 547.0, 626.0, 626.0, 626.0, 0.0515319719077136, 8.05597562675761, 0.03226499580382514], "isController": false}, {"data": ["Start Quiz easy bài 2-0", 7, 0, 0.0, 269.8571428571429, 133, 361, 307.0, 361.0, 361.0, 361.0, 0.05164755707055057, 0.09915927461006095, 0.016622616373013415], "isController": false}]}, function(index, item){
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
    createTable($("#top5ErrorsBySamplerTable"), {"supportsControllersDiscrimination": false, "overall": {"data": ["Total", 946, 0, "", "", "", "", "", "", "", "", "", ""], "isController": false}, "titles": ["Sample", "#Samples", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors"], "items": [{"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}]}, function(index, item){
        return item;
    }, [[0, 0]], 0);

});
