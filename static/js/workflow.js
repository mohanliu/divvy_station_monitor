function draw() {
  var ctx = document.getElementById('canvas').getContext('2d');
  var img = new Image();
  img.onload = function() {
	ctx.canvas.width  = window.innerWidth;
  	ctx.canvas.height = window.innerHeight;
    ctx.drawImage(img, 0, 0);
    ctx.beginPath();
//     ctx.moveTo(0.3*ctx.canvas.width, 0.5*ctx.canvas.height);
//     ctx.lineTo(0.5*ctx.canvas.width, 0.5*ctx.canvas.height);
    ctx.lineTo(103, 76);
    ctx.lineTo(100, 15);
    ctx.stroke();
  };
  img.src = 'https://mdn.mozillademos.org/files/5395/backdrop.png';
}
