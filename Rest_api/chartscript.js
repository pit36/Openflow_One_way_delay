var gradientStroke1 = 'rgba(0, 102, 179, 0.6)',
    gradientStroke2 = 'rgba(0, 98, 95, 0.6)',

    gradientFill1 = 'rgba(0, 102, 179, 0.6)',
    gradientFill2 = 'rgba(0, 98, 95, 0.6)';


var chartArray = []

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

window.onload = function() {
    xmlhttpStart.open("GET", "http://127.0.0.1:5000/user", true);
    xmlhttpStart.send();
}

var xmlhttpStart = new XMLHttpRequest();

var s = new sigma({
settings: {
    doubleClickEnabled: false,
    minEdgeSize: 0.5,
    maxEdgeSize: 4,
    enableEdgeHovering: true,
    edgeHoverColor: 'edge',
    defaultEdgeHoverColor: '#000',
    edgeHoverSizeRatio: 1,
    edgeHoverExtremities: true,
  }}
);
var cam = s.addCamera();
var nodeArray = []

s.bind('overEdge outEdge clickEdge doubleClickEdge rightClickEdge', function(e) {
        console.log(e.data.edge.source.substring(1,), e.data.edge.target.substring(1,));

        });

xmlhttpStart.onreadystatechange = async function() {
    // TODO: check the "states"
    if (this.readyState == 4 && this.status == 200) {
        //console.log(this.responseText)
        var jsonData = JSON.parse(this.responseText);
        //
        // Adding the general plot
        s.addRenderer({
            container: document.getElementById('left'),
            type: 'canvas',
            camera: cam,
            settings: {
                batchEdgesDrawing: true,
                hideEdgesOnMove: false,
                defaultLabelColor: '#000',
                defaultNodeColor: '#666',
                defaultEdgeColor: '#999'
            }
        });
        // Parsing the arrays
        for (var i = 0; i < jsonData.length; i++) {
            var insideArrayData = jsonData[i];

            var IDRec = insideArrayData.IDRec;
            var IDSender = insideArrayData.IDSender;
            document.getElementById("right").innerHTML += '<div><canvas id="chart' + IDRec + '-' + IDSender + '" style="width: 95%"></canvas></div>'

            if (!nodeArray.includes(IDRec)) {
                nodeArray.push(IDRec)
            }
        }

        for (var i = 0; i < nodeArray.length; i++) {
            s.graph.addNode({
                id: 'n' + nodeArray[i],
                label: 'Switch ' + nodeArray[i],
                x: 50 + 0.8 * Math.cos(2 * Math.PI / nodeArray.length * i),
                y: 50 + 0.8 * Math.sin(2 * Math.PI / nodeArray.length * i),
                size: 6
            });
        }
        // Kanten
        for (var i = 0; i < jsonData.length; i++) {
            insideArrayData = jsonData[i];
            var IDRec = insideArrayData.IDRec;
            var IDSender = insideArrayData.IDSender;

            s.graph.addEdge({
                id: 'e' + i,
                source: 'n' + IDSender,
                target: 'n' + IDRec,
                size: 0.5,
                type: 'curvedArrow',
                count: 2,
                color: '#ccc',
                hover_color: '#000'
                //arrow: 'target',

            });
        }

        for (var i = 0; i < jsonData.length; i++) {
            var insideArrayData = jsonData[i];

            var IDRec = insideArrayData.IDRec;
            var IDSender = insideArrayData.IDSender;

            var yChange = 0;

            var addS = true,
                addR = true;
            //document.body.innerHTML+='<div><canvas id="chart'+IDRec+'-'+IDSender+'" width="350" height="200"></canvas></div>'
            var ctx = document.getElementById('chart' + IDRec + '-' + IDSender).getContext("2d");
            var copyOfNerv = JSON.parse(JSON.stringify(nerv))
            var chart = new Chart(ctx, copyOfNerv);

           chart.options.title = {text:IDSender +'-'+ IDRec, display: true}
            chart.update();
            chartArray[i] = chart
            var nodes = s.graph.nodes()
            for (n in nodes) {
                if (nodes[n].id == ('n' + IDRec)) {
                    addR = false;
                }
                if (nodes[n].id == ('n' + IDSender)) {
                    addS = false;
                }
            }
            if ((IDRec % 2) > 0) {
                yChange = 50;
            } else {
                yChange = -50;
            }
            if (addR) {

            }
            if (addS) {
                s.graph.addNode({
                    id: 'n' + IDSender,
                    label: 'Switch ' + IDSender,
                    x: IDSender * 5,
                    y: 100,
                    size: 6
                });
            }

        }

        s.refresh();
    }
};

var xmlhttp = new XMLHttpRequest();
xmlhttp.onreadystatechange = function() {
    // TODO: check the "states"
    if (this.readyState == 4 && this.status == 200) {
        var jsonData = JSON.parse(this.responseText);
        // Parsing the arrays
        for (var i = 0; i < jsonData.length; i++) {
            var insideArrayData = jsonData[i];

            var IDRec = insideArrayData.IDRec;
            var IDSender = insideArrayData.IDSender;

            var bandwithMap = insideArrayData.bandwithMap;
            var latencyMap = insideArrayData.latencyMap;

            addData(chartArray[i], latencyMap.split(';'), 0)
            addData(chartArray[i], bandwithMap.split(';'), 1)
        }
        // addData(myChart, [Math.random()*100, Math.random()*100, Math.random()*100, Math.random()*100, Math.random()*100, Math.random()*100, 42], 0);
    }
};


var nerv = {
    type: 'line',
    data: {
        labels: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
        datasets: [{
                label: "Latency (ms)",
                yAxisID: 'A',
                borderColor: gradientStroke1,
                pointBorderColor: gradientStroke1,
                pointBackgroundColor: gradientStroke1,
                pointHoverBackgroundColor: gradientStroke1,
                pointHoverBorderColor: gradientStroke1,
                pointBorderWidth: 5,
                pointHoverRadius: 5,
                pointHoverBorderWidth: 1,
                pointRadius: 3,
                fill: true,
                backgroundColor: gradientFill1,
                borderWidth: 2,
                data: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            },
            {
                label: "Bandwidth (kB/s)",
                yAxisID: 'B',
                borderColor: gradientStroke2,
                pointBorderColor: gradientStroke2,
                pointBackgroundColor: gradientStroke2,
                pointHoverBackgroundColor: gradientStroke2,
                pointHoverBorderColor: gradientStroke2,
                pointBorderWidth: 5,
                pointHoverRadius: 5,
                pointHoverBorderWidth: 1,
                pointRadius: 3,
                fill: true,
                backgroundColor: gradientFill2,
                borderWidth: 2,
                data: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],

            }
        ]
    },
    options: {
        responsive: false,
        legend: {
            position: "top"
        },
        scales: {
            yAxes: [{
                id: 'A',
                type: 'linear',
                position: 'left',
            }, {
                id: 'B',
                type: 'linear',
                position: 'right',
                ticks: {
                    beginAtZero: true,
                    maxTicksLimit: 5,
                }
            }],
            xAxes: [{
                gridLines: {
                    zeroLineColor: "rgba(255,255,255,0.5)"
                },
                ticks: {
                    padding: 20,
                    fontColor: "rgba(255,255,255,0.5)",
                    fontStyle: "bold"
                }
            }]
        }
    }
}


setInterval(function() {
    xmlhttp.open("GET", "http://127.0.0.1:5000/user", true);
    xmlhttp.send();

}, 2000);

function addData(chart, data, datasetIndex) {

    if(datasetIndex > 0){
    chart.data.labels.shift();
    //if(chart.data.labels[chart.data.labels.length-1] > 15){
    //chart.data.labels =["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"];
    //}
    chart.data.labels.push(parseInt(chart.data.labels[chart.data.labels.length-1])+1);
    }
    chart.data.datasets[datasetIndex].data.push(data[chart.data.labels.length-1]);
    chart.data.datasets[datasetIndex].data.shift();
    //chart.removeData();
    //chart.data.datasets[datasetIndex].data = data;
    chart.update();
}