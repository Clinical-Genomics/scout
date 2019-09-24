var bkgColors = ["#FDB45C", "#949FB1", "#44449B", "#F7464A", "#00b0f0", "#46BFBD"];
var hoverColors = ["#FFC870", "#A8B3C5", "#353578", "#FF5A5E", "#0287b8", "#5AD3D1"];

function createChart(ctx, chartData) {
  //plots the chart
  new Chart(ctx, chartData);
}

function analysisTypeData(analysis_types) {
  //creates data for the general samples (WGS/WES) stats chart
  var labels = analysis_types.map(function (analysis_types) {
    return analysis_types.name.toUpperCase();
  });
  var colors = {
    "bkgColors": {
      "WES": "#46bfbd",
      "WGS": "#fdb45c",
      "PANEL": "#44449B"
    },
    "hoverColors": {
      "WES": "#5ad3d1",
      "WGS": "#ffc870",
      "PANEL": "#353578"
    }
  };
  var bkg = [];
  var hover = [];
  var _iteratorNormalCompletion = true;
  var _didIteratorError = false;
  var _iteratorError = undefined;

  try {
    for (var _iterator = labels[Symbol.iterator](), _step; !(_iteratorNormalCompletion = (_step = _iterator.next()).done); _iteratorNormalCompletion = true) {
      var label = _step.value;
      bkg.push(colors["bkgColors"][label]);
      hover.push(colors["hoverColors"][label]);
    }
  } catch (err) {
    _didIteratorError = true;
    _iteratorError = err;
  } finally {
    try {
      if (!_iteratorNormalCompletion && _iterator.return != null) {
        _iterator.return();
      }
    } finally {
      if (_didIteratorError) {
        throw _iteratorError;
      }
    }
  }

  var chart_data = {
    type: "pie",
    data: {
      labels: labels,
      datasets: [{
        data: analysis_types.map(function (analysis_types) {
          return analysis_types.count;
        }),
        backgroundColor: bkg,
        hoverBackgroundColor: hover
      }]
    },
    options: {
      responsive: true
    }
  };
  return chart_data;
}

function casesType(cases) {
  //creates data for the general cases stats chart
  var labels = cases.map(function (cases) {
    return cases.status;
  });
  var bkg = [];
  var hover = [];
  labels.forEach(function (item, index) {
    bkg.push(bkgColors[index]);
    hover.push(hoverColors[index]);
  });
  var chart_data = {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [{
        data: cases.map(function (cases) {
          return cases.count;
        }),
        backgroundColor: bkg,
        hoverBackgroundColor: hover
      }]
    }
  };
  return chart_data;
}

function pedigreeTypes(pedigree) {
  var labels = pedigree.map(function (pedigree) {
    return pedigree.title;
  });
  var bkg = [];
  var hover = [];
  labels.forEach(function (item, index) {
    bkg.push(bkgColors[index]);
    hover.push(hoverColors[index]);
  });
  var chart_data = {
    type: "pie",
    data: {
      labels: labels,
      datasets: [{
        data: pedigree.map(function (pedigree) {
          return pedigree.count;
        }),
        backgroundColor: bkg,
        hoverBackgroundColor: hover
      }]
    }
  };
  return chart_data;
}

function casesDetailed(overview, all_cases) {
  var labels = overview.map(function (overview) {
    return overview.title;
  });
  var bkg = [];
  var hover = [];
  labels.forEach(function (item, index) {
    bkg.push(bkgColors[index]);
  });
  var chart_data = {
    type: "horizontalBar",
    data: {
      labels: labels,
      datasets: [{
        data: overview.map(function (overview) {
          return overview.count * 100 / all_cases;
        }),
        backgroundColor: bkg,
        hoverBackgroundColor: hover
      }]
    },
    options: {
      tooltips: {
        callbacks: {
          label: function label(tooltipItems) {
            return Math.round(Number(tooltipItems.value) * all_cases / 100);
          }
        }
      },
      scales: {
        xAxes: [{
          ticks: {
            min: 0,
            max: 100,
            callback: function callback(value) {
              return value + "%";
            }
          },
          scaleLabel: {
            display: true,
            labelString: "Case percentage",
            fontSize: 20
          }
        }],
        yAxes: [{
          ticks: {
            fontSize: 20
          }
        }]
      },
      legend: {
        display: false
      }
    }
  };
  return chart_data;
}

function varValidations(variants) {
  var dataSets = [];
  var maxValidations = 0;
  variants.forEach(function (arrayItem) {
    if (arrayItem.title === "Validation ordered") {
      maxValidations = arrayItem.count;
    } else {
      percentValid = arrayItem.count;

      if (maxValidations > 0) {
        percentValid = percentValid * 100 / maxValidations;
      }

      dataSets.push(percentValid);
    }
  });
  var myChart = {
    type: "bar",
    data: {
      datasets: [{
        //true positives
        label: "True Positive",
        data: [dataSets[0]],
        backgroundColor: "#46bfbd"
      }, {
        //false positives
        label: "False Positive",
        data: [dataSets[1]],
        backgroundColor: "#f7464a"
      }]
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
          }
        }],
        yAxes: [{
          stacked: true,
          ticks: {
            min: 0,
            max: 100,
            callback: function callback(value) {
              return value + "%";
            },
            fontSize: 20
          }
        }]
      },
      tooltips: {
        callbacks: {
          label: function label(tooltipItem) {
            return "" + Math.round(Number(tooltipItem.yLabel) * maxValidations / 100);
          }
        }
      }
    }
  };
  return myChart;
}
