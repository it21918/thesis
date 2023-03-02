window.addEventListener("load", (event) => {
var xValues = JSON.parse( document.getElementById('x').value);
var yValues= JSON.parse(document.getElementById('y').value);

new Chart("myChart", {
  type: "line",
  data: {
    labels: xValues,
    datasets: [{
      fill: false,
      lineTension: 0,
      backgroundColor: "rgba(0,0,255,1.0)",
      borderColor: "rgba(0,0,255,0.1)",
      data: yValues
    }]
  },
  options: {
    legend: {display: false},
    scales: {
      yAxes: [{ticks: {min: 0, max:yValues.lenght}}],
      xAxes: [{ticks: {min: 0, max:xValues.lenght}}],    }
  }
});

});
