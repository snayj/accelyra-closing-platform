/**
 * Document Routes
 *
 * Handles PDF generation, OCR processing, and validation
 */

import express from 'express';
import fs from 'fs/promises';
import pdfParse from 'pdf-parse';
import pdfGenerator from '../services/pdfGenerator.js';
import prisma from '../lib/prisma.js';
import { DocumentStatus, DocumentType } from '@prisma/client';

const router = express.Router();

/**
 * POST /api/v1/transactions/:id/generate-documents
 * Generate all closing documents for a transaction
 */
router.post('/transactions/:id/generate-documents', async (req, res) => {
  try {
    const { id: transactionId } = req.params;

    // Verify transaction exists
    const transaction = await prisma.transaction.findUnique({
      where: { id: transactionId },
    });

    if (!transaction) {
      return res.status(404).json({
        error: 'Transaction not found',
        transactionId,
      });
    }

    // Generate all documents
    const documents = await pdfGenerator.generateAllDocuments(transactionId);

    // Fetch created document records
    const documentRecords = await prisma.document.findMany({
      where: {
        transactionId,
        documentType: {
          in: [
            DocumentType.PURCHASE_AGREEMENT,
            DocumentType.PROOF_OF_FUNDS,
            DocumentType.CLOSING_DISCLOSURE,
          ],
        },
      },
      orderBy: { uploadedAt: 'desc' },
      take: 3,
    });

    res.json({
      success: true,
      message: 'Documents generated successfully',
      documents: documentRecords.map((doc) => doc.to_dict()),
      files: {
        purchaseAgreement: documents.purchaseAgreement,
        proofOfFunds: documents.proofOfFunds,
        closingDisclosure: documents.closingDisclosure,
      },
    });
  } catch (error: any) {
    console.error('Error generating documents:', error);
    res.status(500).json({
      error: 'Failed to generate documents',
      details: error.message,
    });
  }
});

/**
 * POST /api/v1/documents/:id/process-ocr
 * Extract text from a document using OCR
 */
router.post('/:id/process-ocr', async (req, res) => {
  try {
    const { id: documentId } = req.params;

    // Fetch document
    const document = await prisma.document.findUnique({
      where: { id: documentId },
      include: { transaction: true },
    });

    if (!document) {
      return res.status(404).json({
        error: 'Document not found',
        documentId,
      });
    }

    if (!document.filePath) {
      return res.status(400).json({
        error: 'Document has no file path',
      });
    }

    // Update status to processing
    await prisma.document.update({
      where: { id: documentId },
      data: { status: DocumentStatus.PROCESSING },
    });

    // Read PDF and extract text
    const dataBuffer = await fs.readFile(document.filePath);
    const pdfData = await pdfParse(dataBuffer);

    // Extract structured data based on document type
    const extractedData = extractStructuredData(
      pdfData.text,
      document.documentType,
      document.transaction
    );

    // Update document with OCR results
    const updatedDocument = await prisma.document.update({
      where: { id: documentId },
      data: {
        ocrText: pdfData.text,
        extractedData: extractedData,
        pageCount: pdfData.numpages,
        status: DocumentStatus.PENDING_REVIEW,
      },
    });

    res.json({
      success: true,
      message: 'OCR processing completed',
      document: {
        id: updatedDocument.id,
        documentType: updatedDocument.documentType,
        pageCount: updatedDocument.pageCount,
        extractedData: updatedDocument.extractedData,
        textLength: pdfData.text.length,
      },
    });
  } catch (error: any) {
    console.error('Error processing OCR:', error);
    res.status(500).json({
      error: 'Failed to process OCR',
      details: error.message,
    });
  }
});

/**
 * POST /api/v1/documents/:id/validate
 * Validate extracted document data
 */
router.post('/:id/validate', async (req, res) => {
  try {
    const { id: documentId } = req.params;

    // Fetch document with transaction
    const document = await prisma.document.findUnique({
      where: { id: documentId },
      include: { transaction: true },
    });

    if (!document) {
      return res.status(404).json({
        error: 'Document not found',
        documentId,
      });
    }

    if (!document.extractedData || Object.keys(document.extractedData as object).length === 0) {
      return res.status(400).json({
        error: 'Document has not been processed with OCR yet',
      });
    }

    // Run validation rules based on document type
    const validationResults = validateDocument(document);

    // Determine if validation passed
    const criticalFailures = validationResults.filter(
      (result) => result.severity === 'critical' && !result.passed
    );
    const validationPassed = criticalFailures.length === 0;

    // Update document with validation results
    const updatedDocument = await prisma.document.update({
      where: { id: documentId },
      data: {
        validationPerformed: true,
        validationPerformedAt: new Date(),
        validationResults: validationResults,
        validationPassed,
        status: validationPassed ? DocumentStatus.APPROVED : DocumentStatus.REJECTED,
        approvedBy: validationPassed ? 'system' : undefined,
        approvedAt: validationPassed ? new Date() : undefined,
        rejectionReason: validationPassed
          ? undefined
          : criticalFailures.map((r) => r.description).join('; '),
      },
    });

    res.json({
      success: true,
      message: validationPassed ? 'Document validation passed' : 'Document validation failed',
      validationPassed,
      validationResults,
      document: {
        id: updatedDocument.id,
        status: updatedDocument.status,
        validationPassed: updatedDocument.validationPassed,
      },
    });
  } catch (error: any) {
    console.error('Error validating document:', error);
    res.status(500).json({
      error: 'Failed to validate document',
      details: error.message,
    });
  }
});

/**
 * GET /api/v1/documents/:id/download
 * Download a document PDF
 */
router.get('/:id/download', async (req, res) => {
  try {
    const { id: documentId } = req.params;

    const document = await prisma.document.findUnique({
      where: { id: documentId },
    });

    if (!document) {
      return res.status(404).json({
        error: 'Document not found',
        documentId,
      });
    }

    if (!document.filePath) {
      return res.status(404).json({
        error: 'Document file not found',
      });
    }

    // Send file
    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', `attachment; filename="${document.filename}"`);
    res.sendFile(document.filePath);
  } catch (error: any) {
    console.error('Error downloading document:', error);
    res.status(500).json({
      error: 'Failed to download document',
      details: error.message,
    });
  }
});

/**
 * GET /api/v1/documents/:id
 * Get document details
 */
router.get('/:id', async (req, res) => {
  try {
    const { id: documentId } = req.params;

    const document = await prisma.document.findUnique({
      where: { id: documentId },
      include: { transaction: true },
    });

    if (!document) {
      return res.status(404).json({
        error: 'Document not found',
        documentId,
      });
    }

    res.json({
      document: {
        id: document.id,
        transactionId: document.transactionId,
        documentType: document.documentType,
        status: document.status,
        filename: document.filename,
        fileSize: document.fileSize,
        pageCount: document.pageCount,
        uploadedAt: document.uploadedAt,
        extractedData: document.extractedData,
        validationPerformed: document.validationPerformed,
        validationResults: document.validationResults,
        validationPassed: document.validationPassed,
      },
    });
  } catch (error: any) {
    console.error('Error fetching document:', error);
    res.status(500).json({
      error: 'Failed to fetch document',
      details: error.message,
    });
  }
});

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Extract structured data from OCR text based on document type
 */
function extractStructuredData(
  ocrText: string,
  documentType: DocumentType,
  transaction: any
): Record<string, any> {
  const text = ocrText.toLowerCase();

  switch (documentType) {
    case DocumentType.PURCHASE_AGREEMENT:
      return {
        propertyAddress: extractPropertyAddress(ocrText),
        purchasePrice: extractAmount(ocrText, 'purchase price'),
        buyerName: extractName(ocrText, 'buyer'),
        sellerName: extractName(ocrText, 'seller'),
        closingDate: extractDate(ocrText, 'closing date'),
        contractDate: extractDate(ocrText, 'contract date'),
      };

    case DocumentType.PROOF_OF_FUNDS:
      return {
        accountHolder: extractAccountHolder(ocrText),
        availableBalance: extractAmount(ocrText, 'available balance') || extractAmount(ocrText, 'current balance'),
        bankName: extractBankName(ocrText),
        accountNumber: extractAccountNumber(ocrText),
        statementDate: extractDate(ocrText, 'statement date'),
        verifiedAmount: extractAmount(ocrText, 'available balance') || extractAmount(ocrText, 'current balance'),
      };

    case DocumentType.CLOSING_DISCLOSURE:
      return {
        propertyAddress: extractPropertyAddress(ocrText),
        salePrice: extractAmount(ocrText, 'sale price'),
        loanAmount: extractAmount(ocrText, 'loan amount'),
        cashToClose: extractAmount(ocrText, 'cash to close'),
        closingDate: extractDate(ocrText, 'closing date'),
      };

    default:
      return {};
  }
}

/**
 * Validate document data
 */
function validateDocument(document: any): any[] {
  const results: any[] = [];
  const extracted = document.extractedData as Record<string, any>;
  const transaction = document.transaction;

  switch (document.documentType) {
    case DocumentType.PURCHASE_AGREEMENT:
      // Validate purchase price matches
      if (extracted.purchasePrice) {
        const matches = Math.abs(extracted.purchasePrice - transaction.purchasePrice) < 100;
        results.push({
          rule_id: 'purchase_price_match',
          description: 'Purchase price matches transaction',
          passed: matches,
          expected: transaction.purchasePrice,
          found: extracted.purchasePrice,
          severity: 'critical',
        });
      }

      // Validate property address
      if (extracted.propertyAddress) {
        const matches = extracted.propertyAddress
          .toLowerCase()
          .includes(transaction.propertyAddress.toLowerCase().split(',')[0]);
        results.push({
          rule_id: 'property_address_match',
          description: 'Property address matches transaction',
          passed: matches,
          expected: transaction.propertyAddress,
          found: extracted.propertyAddress,
          severity: 'critical',
        });
      }
      break;

    case DocumentType.PROOF_OF_FUNDS:
      // Validate sufficient funds (20% down payment)
      const requiredAmount = transaction.purchasePrice * 0.20;
      if (extracted.verifiedAmount !== undefined) {
        const sufficient = extracted.verifiedAmount >= requiredAmount;
        results.push({
          rule_id: 'sufficient_funds',
          description: 'Buyer has sufficient funds for down payment (20%)',
          passed: sufficient,
          expected: requiredAmount,
          found: extracted.verifiedAmount,
          severity: 'critical',
        });
      }

      // Validate account holder name
      if (extracted.accountHolder && transaction.buyer) {
        const matches = extracted.accountHolder
          .toLowerCase()
          .includes(transaction.buyer.name.toLowerCase().split(' ')[0]);
        results.push({
          rule_id: 'account_holder_match',
          description: 'Account holder matches buyer name',
          passed: matches,
          expected: transaction.buyer.name,
          found: extracted.accountHolder,
          severity: 'warning',
        });
      }
      break;

    case DocumentType.CLOSING_DISCLOSURE:
      // Validate sale price
      if (extracted.salePrice) {
        const matches = Math.abs(extracted.salePrice - transaction.purchasePrice) < 100;
        results.push({
          rule_id: 'sale_price_match',
          description: 'Sale price matches transaction',
          passed: matches,
          expected: transaction.purchasePrice,
          found: extracted.salePrice,
          severity: 'critical',
        });
      }
      break;
  }

  return results;
}

// ============================================================================
// TEXT EXTRACTION HELPERS
// ============================================================================

function extractPropertyAddress(text: string): string | null {
  // Look for address patterns (number + street + city, state)
  const addressMatch = text.match(/(\d+\s+[A-Za-z\s]+(?:st|street|ave|avenue|rd|road|dr|drive|ln|lane|blvd|boulevard),\s*[A-Za-z\s]+,\s*[A-Z]{2})/i);
  return addressMatch ? addressMatch[1].trim() : null;
}

function extractAmount(text: string, context?: string): number | null {
  // Look for dollar amounts near the context keyword
  let searchText = text;
  if (context) {
    const contextIndex = text.toLowerCase().indexOf(context.toLowerCase());
    if (contextIndex !== -1) {
      // Search within 200 characters after the context
      searchText = text.substring(contextIndex, contextIndex + 200);
    }
  }

  const amountMatch = searchText.match(/\$\s*([\d,]+(?:\.\d{2})?)/);
  if (amountMatch) {
    return parseFloat(amountMatch[1].replace(/,/g, ''));
  }
  return null;
}

function extractName(text: string, role: string): string | null {
  const roleIndex = text.toLowerCase().indexOf(role.toLowerCase());
  if (roleIndex === -1) return null;

  // Look for name pattern after role (capitalized words)
  const afterRole = text.substring(roleIndex, roleIndex + 100);
  const nameMatch = afterRole.match(/([A-Z][a-z]+\s+[A-Z][a-z]+)/);
  return nameMatch ? nameMatch[1] : null;
}

function extractDate(text: string, context?: string): string | null {
  let searchText = text;
  if (context) {
    const contextIndex = text.toLowerCase().indexOf(context.toLowerCase());
    if (contextIndex !== -1) {
      searchText = text.substring(contextIndex, contextIndex + 100);
    }
  }

  // Match various date formats
  const dateMatch = searchText.match(/(\w+\s+\d{1,2},\s+\d{4}|\d{1,2}\/\d{1,2}\/\d{4})/);
  return dateMatch ? dateMatch[1] : null;
}

function extractAccountHolder(text: string): string | null {
  const holderMatch = text.match(/account\s+holder[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)/i);
  return holderMatch ? holderMatch[1] : null;
}

function extractBankName(text: string): string | null {
  const bankMatch = text.match(/([A-Z][a-z]+\s+(?:National\s+)?Bank)/);
  return bankMatch ? bankMatch[1] : null;
}

function extractAccountNumber(text: string): string | null {
  const accountMatch = text.match(/\*{4}(\d{4})/);
  return accountMatch ? accountMatch[1] : null;
}

export default router;
