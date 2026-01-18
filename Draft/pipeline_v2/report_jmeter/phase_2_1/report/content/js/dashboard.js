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
    createTable($("#apdexTable"), {"supportsControllersDiscrimination": true, "overall": {"data": [0.9530416221985059, 500, 1500, "Total"], "isController": false}, "titles": ["Apdex", "T (Toleration threshold)", "F (Frustration threshold)", "Label"], "items": [{"data": [1.0, 500, 1500, "Login-0"], "isController": false}, {"data": [1.0, 500, 1500, "Login-1"], "isController": false}, {"data": [1.0, 500, 1500, "Login-2"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 1"], "isController": false}, {"data": [1.0, 500, 1500, "View bài 1"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 1-1"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 1-0"], "isController": false}, {"data": [1.0, 500, 1500, "View bài 3"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 3"], "isController": false}, {"data": [1.0, 500, 1500, "View bài 2"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 2"], "isController": false}, {"data": [1.0, 500, 1500, "Get bộ câu hỏi easy 1"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 3-1"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 3-0"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz 1-1"], "isController": false}, {"data": [0.6428571428571429, 500, 1500, "Start Quiz medium bài 2"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz 1-0"], "isController": false}, {"data": [0.85, 500, 1500, "Login"], "isController": false}, {"data": [1.0, 500, 1500, "View Section 1"], "isController": false}, {"data": [1.0, 500, 1500, "Set grade"], "isController": false}, {"data": [1.0, 500, 1500, "View Chủ đề 1"], "isController": false}, {"data": [1.0, 500, 1500, "View Chủ đề 2"], "isController": false}, {"data": [1.0, 500, 1500, "Get login page"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz hard bài 2"], "isController": false}, {"data": [0.9375, 500, 1500, "View Bài 1"], "isController": false}, {"data": [1.0, 500, 1500, "View Grade"], "isController": false}, {"data": [1.0, 500, 1500, "Submit Quiz"], "isController": false}, {"data": [0.6, 500, 1500, "Start Quiz 1"], "isController": false}, {"data": [0.975, 500, 1500, "test login"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 2-0"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz easy bài 2-1"], "isController": false}, {"data": [0.9907407407407407, 500, 1500, "View video bai 1"], "isController": false}, {"data": [0.9791666666666666, 500, 1500, "View video bai 3"], "isController": false}, {"data": [1.0, 500, 1500, "Get bộ câu hỏi medium bài 2"], "isController": false}, {"data": [1.0, 500, 1500, "View video bai 2"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz hard bài 2-0"], "isController": false}, {"data": [1.0, 500, 1500, "Submit câu 2-1"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz hard bài 2-1"], "isController": false}, {"data": [0.7307692307692307, 500, 1500, "View pdf bai 1"], "isController": false}, {"data": [0.6, 500, 1500, "View pdf bai 2"], "isController": false}, {"data": [1.0, 500, 1500, "Debug Sampler"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz medium bài 2-1"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz medium bài 2-0"], "isController": false}, {"data": [1.0, 500, 1500, "test login-0"], "isController": false}, {"data": [1.0, 500, 1500, "Submit Quiz-1"], "isController": false}, {"data": [1.0, 500, 1500, "test login-1"], "isController": false}, {"data": [1.0, 500, 1500, "Submit Quiz-0"], "isController": false}, {"data": [0.5625, 500, 1500, "Start Quiz easy bài 2"], "isController": false}, {"data": [1.0, 500, 1500, "Start Quiz easy bài 2-0"], "isController": false}]}, function(index, item){
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
    createTable($("#statisticsTable"), {"supportsControllersDiscrimination": true, "overall": {"data": ["Total", 937, 0, 0.0, 284.8164354322307, 0, 1274, 277.0, 492.20000000000005, 562.1999999999998, 617.48, 1.1453717568682578, 772.6509498288665, 0.4697431852214039], "isController": false}, "titles": ["Label", "#Samples", "FAIL", "Error %", "Average", "Min", "Max", "Median", "90th pct", "95th pct", "99th pct", "Transactions/s", "Received", "Sent"], "items": [{"data": ["Login-0", 20, 0, 0.0, 137.89999999999998, 99, 240, 128.5, 173.80000000000004, 236.79999999999995, 240.0, 0.419903422212891, 0.944290625656099, 0.14188142977115262], "isController": false}, {"data": ["Login-1", 20, 0, 0.0, 46.900000000000006, 40, 67, 44.0, 60.0, 66.64999999999999, 67.0, 0.42079572471543686, 0.7754311841191693, 0.1450183703633571], "isController": false}, {"data": ["Login-2", 20, 0, 0.0, 307.90000000000003, 276, 412, 295.0, 347.7, 408.79999999999995, 412.0, 0.4182350480970305, 86.91651309598494, 0.13310820524884986], "isController": false}, {"data": ["Submit câu 1", 27, 0, 0.0, 358.962962962963, 343, 412, 356.0, 372.79999999999995, 403.99999999999994, 412.0, 0.048938487945725404, 7.66931845962031, 0.04235034225222172], "isController": false}, {"data": ["View bài 1", 18, 0, 0.0, 267.3333333333333, 252, 288, 266.5, 281.7, 288.0, 288.0, 0.032154972677205164, 6.11481443789535, 0.009340154281345292], "isController": false}, {"data": ["Submit câu 1-1", 27, 0, 0.0, 250.8148148148148, 242, 273, 250.0, 259.0, 270.59999999999997, 273.0, 0.04894833593786825, 7.576024371399125, 0.01533176320970555], "isController": false}, {"data": ["Submit câu 1-0", 27, 0, 0.0, 108.00000000000001, 97, 144, 106.0, 116.4, 133.59999999999994, 144.0, 0.04896076248227439, 0.09486147730940664, 0.027033962675578734], "isController": false}, {"data": ["View bài 3", 12, 0, 0.0, 275.91666666666663, 263, 306, 271.5, 304.5, 306.0, 306.0, 0.0681717473555043, 12.903633554134048, 0.019827948001999704], "isController": false}, {"data": ["Submit câu 3", 27, 0, 0.0, 355.5555555555556, 336, 392, 354.0, 373.4, 391.6, 392.0, 0.05336305853334598, 8.362866373836882, 0.04617927294809158], "isController": false}, {"data": ["View bài 2", 34, 0, 0.0, 265.6176470588235, 251, 294, 263.5, 282.0, 291.75, 294.0, 0.0657459653248044, 12.486789623304624, 0.019197308234488786], "isController": false}, {"data": ["Submit câu 2", 27, 0, 0.0, 361.55555555555554, 343, 389, 358.0, 380.4, 387.8, 389.0, 0.05095656801852554, 7.9857298460875725, 0.04409674647031402], "isController": false}, {"data": ["Get bộ câu hỏi easy 1", 5, 0, 0.0, 285.8, 278, 292, 289.0, 292.0, 292.0, 292.0, 0.015401675702316413, 2.3835898033206013, 0.006241890055137999], "isController": false}, {"data": ["Submit câu 3-1", 27, 0, 0.0, 250.37037037037038, 237, 278, 248.0, 262.6, 272.79999999999995, 278.0, 0.05337434591715906, 8.261222496767887, 0.016718093013693484], "isController": false}, {"data": ["Submit câu 3-0", 27, 0, 0.0, 105.0, 94, 146, 102.0, 114.0, 133.19999999999993, 146.0, 0.05339007181953365, 0.10344326415034645, 0.029479630946072075], "isController": false}, {"data": ["Start Quiz 1-1", 5, 0, 0.0, 247.2, 233, 261, 245.0, 261.0, 261.0, 261.0, 0.014491115497088734, 2.2426699409342135, 0.00442941323299685], "isController": false}, {"data": ["Start Quiz medium bài 2", 7, 0, 0.0, 545.0000000000001, 391, 615, 595.0, 615.0, 615.0, 615.0, 0.04043718372345587, 6.322100942764055, 0.025453762968782493], "isController": false}, {"data": ["Start Quiz 1-0", 5, 0, 0.0, 284.8, 133, 336, 318.0, 336.0, 336.0, 336.0, 0.014496493298271148, 0.027832134594141678, 0.004685878204812256], "isController": false}, {"data": ["Login", 20, 0, 0.0, 494.34999999999997, 447, 720, 468.0, 578.0000000000001, 713.0999999999999, 720.0, 0.41651047523845225, 88.262311789329, 0.41683587404723227], "isController": false}, {"data": ["View Section 1", 5, 0, 0.0, 340.0, 301, 448, 312.0, 448.0, 448.0, 448.0, 0.07317215945676989, 23.006284459513846, 0.02165152765175906], "isController": false}, {"data": ["Set grade", 20, 0, 0.0, 279.19999999999993, 254, 420, 272.5, 331.7000000000001, 415.8499999999999, 420.0, 0.07176278095128742, 11.166099497750237, 0.03216009783061113], "isController": false}, {"data": ["View Chủ đề 1", 52, 0, 0.0, 303.7115384615385, 290, 347, 299.5, 321.7, 329.54999999999995, 347.0, 0.08099738939183422, 20.992482575826017, 0.024082607212505998], "isController": false}, {"data": ["View Chủ đề 2", 12, 0, 0.0, 310.00000000000006, 294, 327, 311.0, 326.7, 327.0, 327.0, 0.0688649901867389, 21.652054077668232, 0.02043308546719157], "isController": false}, {"data": ["Get login page", 20, 0, 0.0, 129.45, 113, 171, 126.5, 143.4, 169.64999999999998, 171.0, 1.0544630147097591, 19.775300521959192, 0.1400458691411399], "isController": false}, {"data": ["Start Quiz hard bài 2", 7, 0, 0.0, 391.1428571428571, 366, 408, 397.0, 408.0, 408.0, 408.0, 0.04100593414446976, 6.410180574390623, 0.0258117710462957], "isController": false}, {"data": ["View Bài 1", 8, 0, 0.0, 320.37499999999994, 260, 688, 268.5, 688.0, 688.0, 688.0, 0.08919015340706386, 16.96102320616304, 0.026042827996789156], "isController": false}, {"data": ["View Grade", 8, 0, 0.0, 296.375, 285, 321, 292.5, 321.0, 321.0, 321.0, 0.09128981091597914, 21.85040345817215, 0.027993164675407668], "isController": false}, {"data": ["Submit Quiz", 27, 0, 0.0, 362.2222222222222, 321, 414, 360.0, 379.59999999999997, 409.2, 414.0, 0.0561160229950992, 9.034880638491227, 0.03701692807380712], "isController": false}, {"data": ["Start Quiz 1", 5, 0, 0.0, 532.0, 373, 593, 573.0, 593.0, 593.0, 593.0, 0.014485531850787433, 2.2696168957070677, 0.009110041515534283], "isController": false}, {"data": ["test login", 20, 0, 0.0, 358.55, 302, 581, 348.5, 356.0, 569.7499999999998, 581.0, 0.2787611852925599, 58.112982235072344, 0.1504874836227804], "isController": false}, {"data": ["Submit câu 2-0", 27, 0, 0.0, 108.29629629629629, 97, 123, 108.0, 117.6, 121.8, 123.0, 0.05098245070752312, 0.09877849824582603, 0.028150249294742764], "isController": false}, {"data": ["Start Quiz easy bài 2-1", 8, 0, 0.0, 252.125, 242, 261, 252.5, 261.0, 261.0, 261.0, 0.048660616530011434, 7.512636078653804, 0.014968841998978128], "isController": false}, {"data": ["View video bai 1", 54, 0, 0.0, 288.7407407407407, 262, 577, 277.0, 307.0, 349.0, 577.0, 0.08488283810484917, 13.168610768566941, 0.024490393502690312], "isController": false}, {"data": ["View video bai 3", 24, 0, 0.0, 305.99999999999994, 262, 764, 275.0, 388.0, 691.75, 764.0, 0.11631795513034882, 18.041664546287276, 0.03360422694602362], "isController": false}, {"data": ["Get bộ câu hỏi medium bài 2", 7, 0, 0.0, 287.4285714285714, 277, 300, 287.0, 300.0, 300.0, 300.0, 0.04140174478781605, 6.393415921188822, 0.016790579254768595], "isController": false}, {"data": ["View video bai 2", 7, 0, 0.0, 278.1428571428571, 273, 286, 277.0, 286.0, 286.0, 286.0, 0.0413491641561817, 6.415823531366295, 0.011923649875952508], "isController": false}, {"data": ["Start Quiz hard bài 2-0", 7, 0, 0.0, 132.42857142857144, 123, 145, 131.0, 145.0, 145.0, 145.0, 0.041067520871100785, 0.07884643167244546, 0.013286213853248147], "isController": false}, {"data": ["Submit câu 2-1", 27, 0, 0.0, 252.81481481481478, 235, 268, 250.0, 266.2, 267.6, 268.0, 0.05096714884106367, 7.888639183614816, 0.01596410261008432], "isController": false}, {"data": ["Start Quiz hard bài 2-1", 7, 0, 0.0, 258.14285714285717, 240, 273, 256.0, 273.0, 273.0, 273.0, 0.04103766671552103, 6.336351998754214, 0.0125551901656163], "isController": false}, {"data": ["View pdf bai 1", 26, 0, 0.0, 528.6923076923076, 437, 1257, 503.0, 581.8, 1022.1499999999991, 1257.0, 0.038050915051332145, 209.36902881899474, 0.012296802625513139], "isController": false}, {"data": ["View pdf bai 2", 60, 0, 0.0, 571.2666666666668, 472, 1274, 554.5, 592.6, 739.3999999999999, 1274.0, 0.11183722464743315, 702.2040903532937, 0.03625972517865996], "isController": false}, {"data": ["Debug Sampler", 20, 0, 0.0, 0.65, 0, 5, 0.0, 1.9000000000000021, 4.849999999999998, 5.0, 0.079156821536988, 0.0672098618020842, 0.0], "isController": false}, {"data": ["Start Quiz medium bài 2-1", 7, 0, 0.0, 253.57142857142858, 238, 262, 256.0, 262.0, 262.0, 262.0, 0.04047248738125661, 6.249916435154403, 0.012382277459137243], "isController": false}, {"data": ["Start Quiz medium bài 2-0", 7, 0, 0.0, 290.85714285714283, 142, 359, 342.0, 359.0, 359.0, 359.0, 0.04049824411184458, 0.07775346476942036, 0.01310204074991177], "isController": false}, {"data": ["test login-0", 20, 0, 0.0, 68.4, 32, 169, 64.5, 67.9, 163.94999999999993, 169.0, 0.27986902129803254, 0.1336347245738994, 0.07540611618762419], "isController": false}, {"data": ["Submit Quiz-1", 27, 0, 0.0, 254.55555555555554, 239, 289, 254.0, 267.2, 280.59999999999997, 289.0, 0.056128505173177225, 8.929239625061586, 0.017142256137236276], "isController": false}, {"data": ["test login-1", 20, 0, 0.0, 289.95, 270, 411, 284.0, 292.9, 405.0999999999999, 411.0, 0.27888557324929586, 58.00574809311989, 0.07541349143821291], "isController": false}, {"data": ["Submit Quiz-0", 27, 0, 0.0, 107.33333333333331, 69, 147, 107.0, 118.19999999999999, 137.39999999999995, 147.0, 0.05614507888383583, 0.10768247605516358, 0.01988877685866204], "isController": false}, {"data": ["Start Quiz easy bài 2", 8, 0, 0.0, 556.625, 405, 615, 576.0, 615.0, 615.0, 615.0, 0.04861803242822763, 7.599404410111335, 0.030766098645987797], "isController": false}, {"data": ["Start Quiz easy bài 2-0", 8, 0, 0.0, 304.375, 144, 360, 328.0, 360.0, 360.0, 360.0, 0.04869527108048719, 0.09349111615648226, 0.015835473896291245], "isController": false}]}, function(index, item){
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
    createTable($("#top5ErrorsBySamplerTable"), {"supportsControllersDiscrimination": false, "overall": {"data": ["Total", 937, 0, "", "", "", "", "", "", "", "", "", ""], "isController": false}, "titles": ["Sample", "#Samples", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors"], "items": [{"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}]}, function(index, item){
        return item;
    }, [[0, 0]], 0);

});
