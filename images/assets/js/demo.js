type = ['','info','success','warning','danger'];


demo = {

    proveedor : 0.0,
    perdida : 0.0,
    experimento: 0.0,
    devolucion: 0.0,
    paso: 0.0,
    labels:[],
    series:[],
    high:0,
    unidad:"",
    initChartDonut: function(){
        Chartist.Pie('#chartPreferences', {
          series: [this.proveedor, this.perdida, this.experimento, this.devolucion, this.paso],
        },
        {
            donut: true,
            donutWidth: 60,
            donutSolid: true,
            total: 100,
            showLabel: false
        });
    },
    initChartLine: function () {
        var dataSales = {
          labels: this.labels,
          series: [this.series]
        };

        var optionsSales = {
          lineSmooth: false,
          low: 0,
          high: this.high,
          showArea: true,
          height: "280px",
          axisX: {
            showGrid: true,
          },
          lineSmooth: Chartist.Interpolation.simple({
            divisor: 3
          }),
          showLine: true,
          showPoint: true,
            fullWidth: true,
            plugins: [
                    Chartist.plugins.ctAxisTitle({
                        axisX: {
                            axisTitle: 'Fecha de ejecución de Transacción',
                            axisClass: 'ct-axis-title',
                            offset: {
                                x: 0,
                                y: 35
                            },
                            textAnchor: 'middle'
                        },
                        axisY: {
                            axisTitle: 'Cantidad ('+this.unidad+')',
                            axisClass: 'ct-axis-title',
                            offset: {
                                x: -60,
                                y: 0
                            },
                            flipTitle: false
                        }
                    })
                ]
        };

        var responsiveSales = [
          ['screen and (max-width: 640px)', {
            axisX: {
              labelInterpolationFnc: function (value) {
                return value[0];
              }
            }
          }]
        ];

        Chartist.Line('#chartHours', dataSales, optionsSales, responsiveSales);
    }
}



