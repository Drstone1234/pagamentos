// server.js
const express = require('express');
const axios = require('axios');
const bodyParser = require('body-parser');
require('dotenv').config();

const app = express();
app.use(bodyParser.json());

const PORT = process.env.PORT || 3000;
const NOWPAYMENTS_API_KEY = process.env.NOWPAYMENTS_API_KEY || 'CF7S7Z0-C5P4MAJ-N4WNSMT-9T6VCF1';
const PDF_LINK = 'https://drive.google.com/file/d/1fYm0-t_OkDlybrhHKZHEEt3PtFn601to/view?usp=drivesdk';

// Rota para criar invoice
app.get('/create-invoice', async (req, res) => {
  try {
    const invoice = await axios.post('https://api.nowpayments.io/v1/invoice', {
      price_amount: 7,
      price_currency: 'usd',
      pay_currency: 'usdt',
      order_id: `ebook-${Date.now()}`,
      order_description: 'E-book Matemática para Programadores',
      success_url: PDF_LINK,
      cancel_url: 'https://ebook-mat-prog.carrd.co/',
    }, {
      headers: { 'x-api-key': NOWPAYMENTS_API_KEY }
    });

    // Redireciona o usuário para o link de pagamento da NOWPayments
    res.redirect(invoice.data.invoice_url);
  } catch (error) {
    console.error('Erro ao criar invoice:', error.response ? error.response.data : error.message);
    res.status(500).send('Erro ao criar invoice');
  }
});

// Webhook para confirmar pagamento (opcional)
app.post('/webhook', (req, res) => {
  const data = req.body;
  console.log('Webhook recebido:', data);

  // Aqui você poderia salvar no banco ou enviar email ao usuário

  res.status(200).send('Webhook recebido');
});

app.listen(PORT, () => {
  console.log(`Servidor rodando na porta ${PORT}`);
});
