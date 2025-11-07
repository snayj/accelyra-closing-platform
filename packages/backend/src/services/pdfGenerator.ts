/**
 * PDF Generation Service
 *
 * Generates professional-looking real estate closing documents
 * using HTML templates and Puppeteer.
 */

import puppeteer from 'puppeteer';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { format } from 'date-fns';
import prisma from '../lib/prisma.js';
import { DocumentType, DocumentStatus } from '@prisma/client';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

interface TransactionData {
  id: string;
  propertyAddress: string;
  propertyType?: string;
  purchasePrice: number;
  downPayment?: number;
  loanAmount?: number;
  earnestMoneyAmount?: number;
  estimatedClosingDate?: Date;
  buyer?: {
    name: string;
    email: string;
  };
  seller?: {
    name: string;
    email: string;
  };
}

interface PDFGeneratorOptions {
  template: 'purchase-agreement' | 'proof-of-funds' | 'closing-disclosure';
  transaction: TransactionData;
  outputDir?: string;
}

export class PDFGeneratorService {
  private templatesDir: string;
  private storageDir: string;

  constructor() {
    this.templatesDir = path.join(__dirname, '..', 'templates');
    this.storageDir = path.join(__dirname, '..', '..', 'storage', 'documents');
  }

  /**
   * Ensure storage directory exists
   */
  private async ensureStorageDir(): Promise<void> {
    try {
      await fs.access(this.storageDir);
    } catch {
      await fs.mkdir(this.storageDir, { recursive: true });
    }
  }

  /**
   * Read and populate HTML template with transaction data
   */
  private async readTemplate(templateName: string, data: Record<string, any>): Promise<string> {
    const templatePath = path.join(this.templatesDir, `${templateName}.html`);
    let html = await fs.readFile(templatePath, 'utf-8');

    // Replace all {{placeholder}} with actual data
    Object.entries(data).forEach(([key, value]) => {
      const regex = new RegExp(`{{${key}}}`, 'g');
      html = html.replace(regex, String(value ?? ''));
    });

    return html;
  }

  /**
   * Generate Purchase Agreement PDF
   */
  async generatePurchaseAgreement(transaction: TransactionData): Promise<string> {
    const downPayment = transaction.downPayment || (transaction.purchasePrice * 0.20);
    const loanAmount = transaction.loanAmount || (transaction.purchasePrice - downPayment);
    const earnestMoney = transaction.earnestMoneyAmount || (transaction.purchasePrice * 0.01); // 1% earnest money

    const templateData = {
      transactionId: transaction.id,
      propertyAddress: transaction.propertyAddress,
      propertyType: transaction.propertyType || 'Single Family Residence',
      legalDescription: `Lot 15, Block 3, ${transaction.propertyAddress.split(',')[1]?.trim() || 'Subdivision'} Addition`,
      purchasePrice: this.formatCurrency(transaction.purchasePrice),
      earnestMoney: this.formatCurrency(earnestMoney),
      downPayment: this.formatCurrency(downPayment),
      loanAmount: this.formatCurrency(loanAmount),
      buyerName: transaction.buyer?.name || 'Buyer Name',
      buyerEmail: transaction.buyer?.email || 'buyer@example.com',
      sellerName: transaction.seller?.name || 'Seller Name',
      sellerEmail: transaction.seller?.email || 'seller@example.com',
      contractDate: format(new Date(), 'MMMM dd, yyyy'),
      closingDate: transaction.estimatedClosingDate
        ? format(transaction.estimatedClosingDate, 'MMMM dd, yyyy')
        : format(new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), 'MMMM dd, yyyy'),
      generatedDate: format(new Date(), 'MMMM dd, yyyy \'at\' hh:mm a'),
    };

    const html = await this.readTemplate('purchase-agreement', templateData);
    const filename = `purchase-agreement-${transaction.id}-${Date.now()}.pdf`;

    return await this.generatePDF(html, filename);
  }

  /**
   * Generate Proof of Funds PDF (Bank Statement)
   */
  async generateProofOfFunds(transaction: TransactionData): Promise<string> {
    const requiredAmount = transaction.downPayment || (transaction.purchasePrice * 0.20);
    const availableBalance = Math.round(requiredAmount * 1.5); // Show 150% of required
    const openingBalance = Math.round(availableBalance * 0.6);
    const deposit1 = Math.round(availableBalance * 0.2);
    const deposit2 = Math.round(availableBalance * 0.2);

    const today = new Date();
    const date1 = new Date(today);
    date1.setDate(date1.getDate() - 30);
    const date2 = new Date(today);
    date2.setDate(date2.getDate() - 20);
    const date3 = new Date(today);
    date3.setDate(date3.getDate() - 15);
    const date4 = new Date(today);
    date4.setDate(date4.getDate() - 5);

    const templateData = {
      bankName: 'First National Bank',
      bankWebsite: 'firstnationalbank',
      accountHolder: transaction.buyer?.name || 'Account Holder',
      accountNumber: String(Math.floor(Math.random() * 10000)).padStart(4, '0'),
      accountType: 'Checking Account',
      statementPeriod: `${format(date1, 'MMM dd, yyyy')} - ${format(today, 'MMM dd, yyyy')}`,
      statementDate: format(today, 'MMMM dd, yyyy'),
      availableBalance: this.formatCurrency(availableBalance),
      transactionId: transaction.id,
      propertyAddress: transaction.propertyAddress,
      requiredAmount: this.formatCurrency(requiredAmount),

      // Transaction history
      date1: format(date1, 'MM/dd/yyyy'),
      date2: format(date2, 'MM/dd/yyyy'),
      date3: format(date3, 'MM/dd/yyyy'),
      date4: format(date4, 'MM/dd/yyyy'),
      openingBalance: this.formatCurrency(openingBalance),
      deposit1: this.formatCurrency(deposit1),
      deposit2: this.formatCurrency(deposit2),
      employer: 'Acme Corporation',
      balance1: this.formatCurrency(openingBalance + deposit1),
      balance2: this.formatCurrency(openingBalance + deposit1 - 200),
      balance3: this.formatCurrency(availableBalance),

      // Summary
      totalDeposits: this.formatCurrency(deposit1 + deposit2),
      totalWithdrawals: this.formatCurrency(200),
      averageBalance: this.formatCurrency(Math.round(availableBalance * 0.9)),

      generatedDate: format(new Date(), 'MMMM dd, yyyy \'at\' hh:mm a'),
    };

    const html = await this.readTemplate('proof-of-funds', templateData);
    const filename = `proof-of-funds-${transaction.id}-${Date.now()}.pdf`;

    return await this.generatePDF(html, filename);
  }

  /**
   * Generate Closing Disclosure PDF
   */
  async generateClosingDisclosure(transaction: TransactionData): Promise<string> {
    const loanAmount = transaction.loanAmount || (transaction.purchasePrice * 0.80);
    const earnestMoney = transaction.earnestMoneyAmount || (transaction.purchasePrice * 0.01);
    const loanOriginationFee = Math.round(loanAmount * 0.01); // 1%
    const titleInsurance = Math.round(transaction.purchasePrice * 0.005); // 0.5%
    const closingFee = 500;
    const recordingFeeDeed = 125;
    const recordingFeeMortgage = 150;
    const transferTax = Math.round(transaction.purchasePrice * 0.002); // 0.2%
    const prepaidTaxes = Math.round(transaction.purchasePrice * 0.01 * 0.5); // 6 months property tax
    const dailyInterest = Math.round((loanAmount * 0.065) / 365); // 6.5% annual rate
    const prepaidDays = 15;
    const prepaidInterest = dailyInterest * prepaidDays;

    const buyerClosingCosts = loanOriginationFee + 500 + 50 + 25 + titleInsurance + closingFee +
                               300 + recordingFeeMortgage + 1200 + prepaidTaxes + prepaidInterest + 400 + 250;
    const sellerClosingCosts = closingFee + recordingFeeDeed + transferTax;
    const cashToClose = transaction.purchasePrice - loanAmount + buyerClosingCosts - earnestMoney;

    const closingDate = transaction.estimatedClosingDate || new Date(Date.now() + 30 * 24 * 60 * 60 * 1000);

    const templateData = {
      transactionId: transaction.id,
      closingDate: format(closingDate, 'MMMM dd, yyyy'),
      disbursementDate: format(closingDate, 'MMMM dd, yyyy'),
      propertyAddress: transaction.propertyAddress,
      purchasePrice: this.formatCurrency(transaction.purchasePrice),
      buyerName: transaction.buyer?.name || 'Buyer Name',
      buyerEmail: transaction.buyer?.email || 'buyer@example.com',
      sellerName: transaction.seller?.name || 'Seller Name',
      sellerEmail: transaction.seller?.email || 'seller@example.com',

      // Loan details
      loanAmount: this.formatCurrency(loanAmount),
      loanOriginationFee: this.formatCurrency(loanOriginationFee),

      // Title & closing costs
      titleInsurance: this.formatCurrency(titleInsurance),
      closingFee: this.formatCurrency(closingFee),

      // Government fees
      recordingFeeDeed: this.formatCurrency(recordingFeeDeed),
      recordingFeeMortgage: this.formatCurrency(recordingFeeMortgage),
      transferTax: this.formatCurrency(transferTax),

      // Prepaids
      prepaidTaxes: this.formatCurrency(prepaidTaxes),
      dailyInterest: this.formatCurrency(dailyInterest),
      prepaidDays: String(prepaidDays),
      prepaidInterest: this.formatCurrency(prepaidInterest),

      // Totals
      buyerClosingCosts: this.formatCurrency(buyerClosingCosts),
      sellerClosingCosts: this.formatCurrency(sellerClosingCosts),
      earnestMoney: this.formatCurrency(earnestMoney),
      cashToClose: this.formatCurrency(cashToClose),

      generatedDate: format(new Date(), 'MMMM dd, yyyy \'at\' hh:mm a'),
    };

    const html = await this.readTemplate('closing-disclosure', templateData);
    const filename = `closing-disclosure-${transaction.id}-${Date.now()}.pdf`;

    return await this.generatePDF(html, filename);
  }

  /**
   * Generate PDF from HTML using Puppeteer
   */
  private async generatePDF(html: string, filename: string): Promise<string> {
    await this.ensureStorageDir();

    const outputPath = path.join(this.storageDir, filename);

    const browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
    });

    try {
      const page = await browser.newPage();
      await page.setContent(html, { waitUntil: 'networkidle0' });

      await page.pdf({
        path: outputPath,
        format: 'Letter',
        printBackground: true,
        margin: {
          top: '0.5in',
          right: '0.5in',
          bottom: '0.5in',
          left: '0.5in',
        },
      });

      return outputPath;
    } finally {
      await browser.close();
    }
  }

  /**
   * Generate all documents for a transaction
   */
  async generateAllDocuments(transactionId: string): Promise<{
    purchaseAgreement: string;
    proofOfFunds: string;
    closingDisclosure: string;
  }> {
    // Fetch transaction with related data
    const transaction = await prisma.transaction.findUnique({
      where: { id: transactionId },
      include: {
        buyer: true,
        seller: true,
      },
    });

    if (!transaction) {
      throw new Error(`Transaction ${transactionId} not found`);
    }

    // Generate all three documents
    const [purchaseAgreementPath, proofOfFundsPath, closingDisclosurePath] = await Promise.all([
      this.generatePurchaseAgreement(transaction),
      this.generateProofOfFunds(transaction),
      this.generateClosingDisclosure(transaction),
    ]);

    // Create document records in database
    const timestamp = new Date();

    await Promise.all([
      this.createDocumentRecord(transactionId, DocumentType.PURCHASE_AGREEMENT, purchaseAgreementPath),
      this.createDocumentRecord(transactionId, DocumentType.PROOF_OF_FUNDS, proofOfFundsPath),
      this.createDocumentRecord(transactionId, DocumentType.CLOSING_DISCLOSURE, closingDisclosurePath),
    ]);

    return {
      purchaseAgreement: purchaseAgreementPath,
      proofOfFunds: proofOfFundsPath,
      closingDisclosure: closingDisclosurePath,
    };
  }

  /**
   * Create a document record in the database
   */
  private async createDocumentRecord(
    transactionId: string,
    documentType: DocumentType,
    filePath: string
  ): Promise<void> {
    const filename = path.basename(filePath);
    const stats = await fs.stat(filePath);

    // Generate document ID
    const count = await prisma.document.count();
    const documentId = `DOC-${new Date().getFullYear()}-${String(count + 1).padStart(3, '0')}`;

    await prisma.document.create({
      data: {
        id: documentId,
        transactionId,
        documentType,
        status: DocumentStatus.UPLOADED,
        filename,
        filePath,
        fileSize: stats.size,
        mimeType: 'application/pdf',
        pageCount: 1, // Will be updated by OCR service
        uploadedBy: 'system',
        uploadedAt: new Date(),
      },
    });
  }

  /**
   * Format number as currency
   */
  private formatCurrency(amount: number): string {
    return amount.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  }
}

export default new PDFGeneratorService();
