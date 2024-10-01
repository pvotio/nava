const express = require('express');
const puppeteer = require('puppeteer');
const path = require('path');
const app = express();

app.use(express.json({ limit: '100mb' }));
app.use(express.urlencoded({ extended: true, limit: '100mb' }));

const generatePDF = async (htmlContent, pageSize, landscape, headerContent, footerContent, outputFilename) => {
    try {
        const browser = await puppeteer.launch({
            args: ['--no-sandbox', '--disable-setuid-sandbox'],
            headless: "new"
        });

        const page = await browser.newPage();
        await page.setContent(htmlContent);

        const pdfOptions = {
            format: pageSize,
            printBackground: false,
            preferCSSPageSize: true,
            landscape: landscape === 'true',
            displayHeaderFooter: !!headerContent || !!footerContent,
            headerTemplate: headerContent || '<span></span>',
            footerTemplate: footerContent || '<span></span>'
        };

        const outputPath = path.join(__dirname, '/files/', `${outputFilename}.pdf`);
        console.log(`PDF: ${outputPath}`);
        await page.pdf({ path: outputPath, ...pdfOptions });
        await browser.close();

        return outputPath;
    } catch (error) {
        console.error('Error generating PDF:', error);
        throw new Error(error.message);
    }
}

app.post('/generate-pdf', async (req, res) => {
    const { htmlContent, pageSize, landscape, headerContent, footerContent, outputFilename } = req.body;

    if (!htmlContent || !landscape || !outputFilename || !pageSize) {
        return res.status(400).json({ 
            status: 'error',
            message: 'Missing required fields: htmlContent, landscape, and outputFilename are required.'
        });
    }

    try {
        const pdfPath = await generatePDF(htmlContent, pageSize, landscape, headerContent, footerContent, outputFilename);
        res.json({ status: 'success', path: pdfPath });
    } catch (error) {
        res.status(500).json({
            status: 'error',
            message: 'Error generating PDF: ' + error.message
        });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
