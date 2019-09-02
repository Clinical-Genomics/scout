const bkgColors = [ "#FDB45C", "#949FB1", "#44449B", "#F7464A", "#00b0f0", "#46BFBD"];
const hoverColors = [ "#FFC870", "#A8B3C5", "#353578", "#FF5A5E", "#0287b8", "#5AD3D1"];

function createChart(ctx,chartData){
  //plots the chart
  new Chart(ctx, chartData);
}

function analysisTypeData(analysis_types){
  //creates data for the general samples (WGS/WES) stats chart
  let labels = analysis_types.map(analysis_types => analysis_types.name.toUpperCase());
  let colors = {
    'bkgColors' : {
      'WES' : '#46bfbd',
      'WGS' : '#fdb45c',
      'PANEL': '#44449B'
    },
    'hoverColors' : {
      'WES' : '#5ad3d1',
      'WGS' : '#ffc870',
      'PANEL': '#353578'
    },
  };
  let bkg = []
  let hover = []
  for(let label of labels) {
    bkg.push(colors['bkgColors'][label]);
    hover.push(colors['hoverColors'][label]);
  }
  let chart_data = {
    type: 'pie',
    data: {
      labels: labels,
      datasets: [{
        data: analysis_types.map(analysis_types => analysis_types.count),
        backgroundColor: bkg,
        hoverBackgroundColor: hover
      }],
    },
    options: {responsive: true}
  };
  return chart_data;
}

function casesType(cases){
  //creates data for the general cases stats chart
  let labels = cases.map(cases => cases.status);
  let bkg = []
  let hover = []
  labels.forEach(function (item, index) {
    bkg.push(bkgColors[index])
    hover.push(hoverColors[index])
  });
  let chart_data = {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: cases.map(cases => cases.count),
        backgroundColor: bkg,
        hoverBackgroundColor: hover
      }],
    },
  };
  return chart_data;
}

function pedigreeTypes(pedigree){
  let labels = pedigree.map(pedigree => pedigree.title);
  let bkg = []
  let hover = []
  labels.forEach(function (item, index) {
    bkg.push(bkgColors[index]);
    hover.push(hoverColors[index]);
  });
  let chart_data = {
    type: 'pie',
    data: {
      labels: labels,
      datasets: [{
        data: pedigree.map(pedigree => pedigree.count),
        backgroundColor: bkg,
        hoverBackgroundColor: hover
      }],
    },
  };
  return chart_data;
}

function casesDetailed(overview, all_cases){
  let labels = overview.map(overview => overview.title);
  let bkg = []
  let hover = []
  labels.forEach(function (item, index) {
    bkg.push(bkgColors[index])
  });
  let chart_data = {
    type: 'horizontalBar',
    data: {
      labels: labels,
      datasets: [{
        data: overview.map(overview => (overview.count*100)/all_cases),
        backgroundColor: bkg,
        hoverBackgroundColor: hover
      }],
    },
    options: {
      tooltips: {
        callbacks: {
            label: function(tooltipItems) {
                return Math.round(Number(tooltipItems.value) * all_cases / 100)
            }
        }
      },
      scales: {
        xAxes: [{
             ticks: {
                 min: 0,
                 max: 100,
                 callback: function(value) {
                     return value + "%"
                 }
             },
             scaleLabel: {
                 display: true,
                 labelString: "Case percentage",
                 fontSize: 20
             },
         }],
         yAxes: [{
                   ticks: {
                   fontSize: 20
               }
            }]
      },
      legend: {display: false}
    }
  };
  return chart_data;
}

function varValidations(variants){
  let dataSets = [];
  let maxValidations = 0;

  variants.forEach(function (arrayItem) {
    if (arrayItem.title === 'Validation ordered'){
      maxValidations = arrayItem.count;
    }
    else{
      percentValid = arrayItem.count;
      if(maxValidations > 0){
        percentValid = percentValid * 100 / maxValidations;
      }
      dataSets.push(percentValid);
    }
  });

  var myChart = {
    type: 'bar',
    data: {
      datasets: [
        { //true positives
          label: 'True Positive',
          data: [dataSets[0]],
          backgroundColor: '#46bfbd',
        },
        { //false positives
          label: 'False Positive',
          data: [dataSets[1]],
          backgroundColor: '#f7464a',
        }
      ]
    },
    options: {
      legend: {
        labels: {
            fontSize: 20
        }
      },
      scales: {
        xAxes: [{
          stacked: true,
          scaleLabel: {
              display: true,
              labelString: "Verifications",
              fontSize: 20
          },
        }],
        yAxes: [
          {
            stacked: true ,
            ticks: {
              min: 0,
              max: 100,
              callback: function(value) {
                  return value + "%"
              },
              fontSize: 20
          }},
        ],

      },
      tooltips: {
        callbacks: {
          label: function(tooltipItem) {
            return '' + Math.round(Number(tooltipItem.yLabel) * maxValidations / 100)
          }
        }
      }
    },
  };
  return myChart;
}
