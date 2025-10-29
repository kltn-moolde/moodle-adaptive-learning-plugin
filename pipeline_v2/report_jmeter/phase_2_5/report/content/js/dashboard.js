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
    createTable($("#apdexTable"), {"supportsControllersDiscrimination": true, "overall": {"data": [0.9397321428571429, 500, 1500, "Total"], "isController": false}, "titles": ["Apdex", "T (Toleration threshold)", "F (Frustration threshold)", "Label"], "items": [{"data": [1.0, 500, 1500, "Login-0"], "isController": false}, {"data": [1.0, 500, 1500, "Login-1"], "isController": false}, {"data": [1.0, 500, 1500, "Login-2"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 1"], "isController": false}, {"data": [1.0, 500, 1500, "View bài 1"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 1-1"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 1-0"], "isController": false}, {"data": [1.0, 500, 1500, "View bài 3"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 3"], "isController": false}, {"data": [1.0, 500, 1500, "View bài 2"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 2"], "isController": false}, {"data": [1.0, 500, 1500, "Get bộ câu hỏi easy 1"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 3-1"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 3-0"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz 1-1"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz medium bài 2"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz 1-0"], "isController": false}, {"data": [1.0, 500, 1500, "Login"], "isController": false}, {"data": [1.0, 500, 1500, "View Section 1"], "isController": false}, {"data": [1.0, 500, 1500, "Set grade"], "isController": false}, {"data": [0.9919354838709677, 500, 1500, "View Chủ đề 1"], "isController": false}, {"data": [1.0, 500, 1500, "View Chủ đề 2"], "isController": false}, {"data": [1.0, 500, 1500, "Get login page"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz hard bài 2"], "isController": false}, {"data": [1.0, 500, 1500, "View Bài 1"], "isController": false}, {"data": [1.0, 500, 1500, "View Grade"], "isController": false}, {"data": [1.0, 500, 1500, "Submit Quiz"], "isController": false}, {"data": [0.8333333333333334, 500, 1500, "Start Quiz 1"], "isController": false}, {"data": [1.0, 500, 1500, "test login"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 2-0"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz easy bài 2-1"], "isController": false}, {"data": [1.0, 500, 1500, "View video bai 1"], "isController": false}, {"data": [1.0, 500, 1500, "View video bai 3"], "isController": false}, {"data": [1.0, 500, 1500, "Get bộ câu hỏi medium bài 2"], "isController": false}, {"data": [1.0, 500, 1500, "View video bai 2"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz hard bài 2-0"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 2-1"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz hard bài 2-1"], "isController": false}, {"data": [0.5961538461538461, 500, 1500, "View pdf bai 1"], "isController": false}, {"data": [0.524390243902439, 500, 1500, "View pdf bai 2"], "isController": false}, {"data": [1.0, 500, 1500, "Debug Sampler"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz medium bài 2-1"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz medium bài 2-0"], "isController": false}, {"data": [1.0, 500, 1500, "test login-0"], "isController": false}, {"data": [1.0, 500, 1500, "Submit Quiz-1"], "isController": false}, {"data": [1.0, 500, 1500, "test login-1"], "isController": false}, {"data": [1.0, 500, 1500, "Submit Quiz-0"], "isController": false}, {"data": [0.7, 500, 1500, "Start Quiz easy bài 2"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz easy bài 2-0"], "isController": false}]}, function(index, item){
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
    createTable($("#statisticsTable"), {"supportsControllersDiscrimination": true, "overall": {"data": ["Total", 896, 0, 0.0, 302.8225446428571, 0, 4888, 282.0, 520.3000000000001, 561.15, 717.6899999999994, 1.1117563268365074, 946.64410805983, 0.45027449586317453], "isController": false}, "titles": ["Label", "#Samples", "FAIL", "Error %", "Average", "Min", "Max", "Median", "90th pct", "95th pct", "99th pct", "Transactions/s", "Received", "Sent"], "items": [{"data": ["Login-0", 20, 0, 0.0, 121.45000000000002, 92, 139, 122.5, 133.60000000000002, 138.75, 139.0, 0.4198417196716838, 0.9435778648949346, 0.14186058106094002], "isController": false}, {"data": ["Login-1", 20, 0, 0.0, 44.5, 41, 52, 44.0, 49.60000000000001, 51.9, 52.0, 0.4202828503582911, 0.7744860728770462, 0.14436962169289932], "isController": false}, {"data": ["Login-2", 20, 0, 0.0, 292.15, 275, 318, 289.5, 306.7, 317.45, 318.0, 0.4180339861630751, 86.87003421346905, 0.13267680224902284], "isController": false}, {"data": ["Submit câu 1", 24, 0, 0.0, 372.4583333333333, 344, 454, 367.0, 412.5, 448.5, 454.0, 0.045081428329920924, 7.065272023569134, 0.03928115666735541], "isController": false}, {"data": ["View bài 1", 16, 0, 0.0, 266.5625, 254, 278, 267.0, 276.6, 278.0, 278.0, 0.029841448653124866, 5.674763821253452, 0.008618758241368827], "isController": false}, {"data": ["Submit câu 1-1", 24, 0, 0.0, 261.08333333333337, 242, 317, 256.5, 289.0, 313.25, 317.0, 0.045090660409085014, 6.979355743117568, 0.014090831377839069], "isController": false}, {"data": ["Submit câu 1-0", 24, 0, 0.0, 110.91666666666666, 102, 136, 109.0, 125.5, 134.5, 136.0, 0.04510303223927159, 0.08738712496358869, 0.025205283397385904], "isController": false}, {"data": ["View bài 3", 4, 0, 0.0, 274.5, 268, 288, 271.0, 288.0, 288.0, 288.0, 0.0976324139614352, 18.479985355137906, 0.028317213814986576], "isController": false}, {"data": ["Submit câu 3", 24, 0, 0.0, 369.7916666666667, 339, 449, 357.0, 445.0, 448.25, 449.0, 0.049438665156040784, 7.748158924709033, 0.04307778221238027], "isController": false}, {"data": ["View bài 2", 46, 0, 0.0, 271.17391304347825, 253, 329, 267.5, 294.6, 314.04999999999995, 329.0, 0.0894254415381176, 16.983763997025633, 0.02600901301528981], "isController": false}, {"data": ["Submit câu 2", 24, 0, 0.0, 373.25, 348, 437, 368.5, 413.0, 431.25, 437.0, 0.047110182866026494, 7.3832349121051575, 0.04104888736544154], "isController": false}, {"data": ["Get bộ câu hỏi easy 1", 6, 0, 0.0, 301.0, 287, 339, 295.0, 339.0, 339.0, 339.0, 0.01889234198917469, 2.9237313693956657, 0.0076319649767466755], "isController": false}, {"data": ["Submit câu 3-1", 24, 0, 0.0, 258.70833333333337, 238, 309, 250.0, 293.5, 306.0, 309.0, 0.04944966642079194, 7.654076355564736, 0.01545302075649748], "isController": false}, {"data": ["Submit câu 3-0", 24, 0, 0.0, 110.79166666666666, 79, 156, 107.0, 143.0, 153.5, 156.0, 0.04946729902363918, 0.09584087902875081, 0.027644201041286644], "isController": false}, {"data": ["Start Quiz 1-1", 6, 0, 0.0, 262.1666666666667, 243, 313, 254.0, 313.0, 313.0, 313.0, 0.018039958508095432, 2.7918186439212853, 0.005490677475608472], "isController": false}, {"data": ["Start Quiz medium bài 2", 4, 0, 0.0, 398.0, 393, 410, 394.5, 410.0, 410.0, 410.0, 0.09961895748760989, 15.574801384703509, 0.06265098498244216], "isController": false}, {"data": ["Start Quiz 1-0", 6, 0, 0.0, 236.16666666666669, 161, 390, 189.0, 390.0, 390.0, 390.0, 0.018043104977791945, 0.03464135193978415, 0.005808799096040441], "isController": false}, {"data": ["Login", 20, 0, 0.0, 459.5, 426, 487, 458.0, 477.9, 486.55, 487.0, 0.41674480631785127, 88.30671864255798, 0.41623608463045153], "isController": false}, {"data": ["View Section 1", 6, 0, 0.0, 324.0, 294, 417, 309.0, 417.0, 417.0, 417.0, 0.09034919965667304, 28.40658833892996, 0.026616544820732127], "isController": false}, {"data": ["Set grade", 20, 0, 0.0, 274.1, 258, 355, 266.5, 319.1000000000001, 353.34999999999997, 355.0, 0.07881524917441027, 12.263164024631735, 0.03523210967733037], "isController": false}, {"data": ["View Chủ đề 1", 62, 0, 0.0, 313.258064516129, 288, 501, 303.0, 357.1, 392.7499999999998, 501.0, 0.10017174607431774, 25.961623517417767, 0.029669063652681935], "isController": false}, {"data": ["View Chủ đề 2", 4, 0, 0.0, 311.5, 299, 337, 305.0, 337.0, 337.0, 337.0, 0.09283327144448571, 29.187995352534347, 0.027469219968436688], "isController": false}, {"data": ["Get login page", 20, 0, 0.0, 129.65, 116, 157, 129.0, 146.60000000000002, 156.54999999999998, 157.0, 1.0535742506453143, 19.758632724016223, 0.13992783016383079], "isController": false}, {"data": ["Start Quiz hard bài 2", 4, 0, 0.0, 424.0, 395, 451, 425.0, 451.0, 451.0, 451.0, 0.1000450202591166, 15.639361931619229, 0.06291893852233506], "isController": false}, {"data": ["View Bài 1", 10, 0, 0.0, 270.99999999999994, 261, 295, 268.5, 293.4, 295.0, 295.0, 0.11528573569592235, 21.923102522884218, 0.03352743368188054], "isController": false}, {"data": ["View Grade", 10, 0, 0.0, 309.7, 288, 360, 306.0, 356.1, 360.0, 360.0, 0.1180595728604654, 28.26821179592222, 0.03602892238173382], "isController": false}, {"data": ["Submit Quiz", 24, 0, 0.0, 378.99999999999994, 350, 425, 373.0, 420.5, 424.25, 425.0, 0.05226275973502781, 8.400634679498626, 0.03439951177871947], "isController": false}, {"data": ["Start Quiz 1", 6, 0, 0.0, 498.5, 406, 703, 452.0, 703.0, 703.0, 703.0, 0.018029929683274236, 2.8248826645982335, 0.011292182522988161], "isController": false}, {"data": ["test login", 20, 0, 0.0, 352.65, 304, 375, 356.5, 371.0, 374.85, 375.0, 0.2786912658157293, 58.09527637899922, 0.14995985103951842], "isController": false}, {"data": ["Submit câu 2-0", 24, 0, 0.0, 114.29166666666666, 102, 134, 110.0, 131.0, 133.5, 134.0, 0.047137200678775686, 0.0913283263151279, 0.026342053797294325], "isController": false}, {"data": ["Start Quiz easy bài 2-1", 10, 0, 0.0, 251.3, 245, 259, 250.5, 258.6, 259.0, 259.0, 0.07804147123781577, 12.048223715144728, 0.023915443041432217], "isController": false}, {"data": ["View video bai 1", 48, 0, 0.0, 280.85416666666663, 262, 335, 275.5, 302.1, 329.04999999999995, 335.0, 0.07939330284409966, 12.31671957830578, 0.022775178428178004], "isController": false}, {"data": ["View video bai 3", 8, 0, 0.0, 271.125, 262, 279, 270.0, 279.0, 279.0, 279.0, 0.10942565210849553, 16.972623924551016, 0.03152399157422479], "isController": false}, {"data": ["Get bộ câu hỏi medium bài 2", 4, 0, 0.0, 298.25, 286, 309, 299.0, 309.0, 309.0, 309.0, 0.10116849613030503, 15.622826458090952, 0.04100090419343417], "isController": false}, {"data": ["View video bai 2", 4, 0, 0.0, 273.25, 260, 294, 269.5, 294.0, 294.0, 294.0, 0.10218940806785376, 15.855924111590832, 0.029439331425797716], "isController": false}, {"data": ["Start Quiz hard bài 2-0", 4, 0, 0.0, 158.25, 142, 178, 156.5, 178.0, 178.0, 178.0, 0.1007100055390503, 0.19335534266579382, 0.03255372249357973], "isController": false}, {"data": ["Submit câu 2-1", 24, 0, 0.0, 258.75, 240, 303, 256.0, 289.5, 300.25, 303.0, 0.04712155988070392, 7.293719926259667, 0.014725487462719974], "isController": false}, {"data": ["Start Quiz hard bài 2-1", 4, 0, 0.0, 265.25, 242, 290, 264.5, 290.0, 290.0, 290.0, 0.10049241282283188, 15.516362206059691, 0.030716919153853883], "isController": false}, {"data": ["View pdf bai 1", 26, 0, 0.0, 681.8846153846154, 446, 4888, 516.5, 565.3000000000001, 3387.549999999994, 4888.0, 0.039521786384744594, 217.4622613254619, 0.012718699885234813], "isController": false}, {"data": ["View pdf bai 2", 82, 0, 0.0, 639.3658536585366, 473, 4829, 558.0, 713.1, 1008.4499999999985, 4829.0, 0.15612683591831142, 980.2899092084368, 0.0504407489137761], "isController": false}, {"data": ["Debug Sampler", 20, 0, 0.0, 0.7499999999999999, 0, 3, 1.0, 1.9000000000000021, 2.9499999999999993, 3.0, 0.08771429699183818, 0.07352068467587375, 0.0], "isController": false}, {"data": ["Start Quiz medium bài 2-1", 4, 0, 0.0, 251.75, 248, 256, 251.5, 256.0, 256.0, 256.0, 0.10002000400080016, 15.445471906881377, 0.03057252075415083], "isController": false}, {"data": ["Start Quiz medium bài 2-0", 4, 0, 0.0, 146.25, 138, 161, 143.0, 161.0, 161.0, 161.0, 0.10023806540533768, 0.19244925447938854, 0.032401171532389424], "isController": false}, {"data": ["test login-0", 20, 0, 0.0, 62.9, 32, 67, 64.0, 66.9, 67.0, 67.0, 0.27981028862431273, 0.13360668029575948, 0.07514436462078711], "isController": false}, {"data": ["Submit Quiz-1", 24, 0, 0.0, 266.5, 247, 306, 262.5, 297.5, 304.75, 306.0, 0.0522752816330798, 8.30238720042452, 0.015927624872579], "isController": false}, {"data": ["test login-1", 20, 0, 0.0, 289.3, 269, 311, 290.5, 306.1, 310.8, 311.0, 0.2788155913678693, 57.98806124707244, 0.07514951486087101], "isController": false}, {"data": ["Submit Quiz-0", 24, 0, 0.0, 112.08333333333334, 102, 146, 109.0, 130.0, 142.0, 146.0, 0.05229703846229275, 0.1003019575162829, 0.01848782023764646], "isController": false}, {"data": ["Start Quiz easy bài 2", 10, 0, 0.0, 519.0, 385, 615, 568.5, 613.6, 615.0, 615.0, 0.07793989275470757, 12.182180297866784, 0.04913866676019454], "isController": false}, {"data": ["Start Quiz easy bài 2-0", 10, 0, 0.0, 267.4, 129, 365, 319.0, 363.5, 365.0, 365.0, 0.07809205491433302, 0.1499306444937292, 0.025303656074780953], "isController": false}]}, function(index, item){
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
    createTable($("#top5ErrorsBySamplerTable"), {"supportsControllersDiscrimination": false, "overall": {"data": ["Total", 896, 0, "", "", "", "", "", "", "", "", "", ""], "isController": false}, "titles": ["Sample", "#Samples", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors"], "items": [{"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}]}, function(index, item){
        return item;
    }, [[0, 0]], 0);

});
