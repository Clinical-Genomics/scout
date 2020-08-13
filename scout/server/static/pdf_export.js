/* eslint-disable no-unused-vars */
var generatePDF = () => {

		let htmlWidth = $('.container').width();
		let htmlHeight = $('.container').height();
		let topLeftMargin = 15;
		let pdfWidth = htmlWidth+(topLeftMargin*2);
		let pdfHeight = (pdfWidth*1.5)+(topLeftMargin*2);
		let canvasWidth = htmlWidth;
		let canvasHeight = htmlHeight;

		let pdfPages = Math.ceil(htmlHeight/pdfHeight)-1;

		html2canvas($('.container')[0],{allowTaint:true}).then(function(canvas) {
			canvas.getContext('2d');

			let imgData = canvas.toDataURL('image/jpeg', 1.0);
			let pdf = new jsPDF('p', 'pt',  [pdfWidth, pdfHeight]);
			pdf.addImage(imgData, 'JPG', topLeftMargin, topLeftMargin,canvasWidth,canvasHeight);

			for (var i = 1; i <= pdfPages; i++) {
					pdf.addPage(pdfWidth, pdfHeight);
					pdf.addImage(imgData, 'JPG', topLeftMargin, -(pdfHeight*i)+(topLeftMargin*4),canvasWidth,canvasHeight);
			}

			let today = new Date();
			let date = `${today.getFullYear()}_${(today.getMonth()+1)}_${today.getDate()}`;

			pdf.save(`${date}_scout_report.pdf`);
    });
};
