import { useState } from 'react';
import { FileText, Download, ScanEye, CheckCircle, XCircle, Loader2, PlayCircle } from 'lucide-react';
import Button from '../ui/Button';
import Card, { CardContent, CardHeader, CardTitle } from '../ui/Card';
import { cn } from '../../lib/utils';

interface Document {
  id: string;
  documentType: string;
  filename: string;
  status: string;
  fileSize?: number;
  pageCount?: number;
  uploadedAt?: string;
  extractedData?: Record<string, any>;
  validationPerformed?: boolean;
  validationResults?: ValidationResult[];
  validationPassed?: boolean;
}

interface ValidationResult {
  rule_id: string;
  description: string;
  passed: boolean;
  expected?: any;
  found?: any;
  severity: 'critical' | 'warning';
}

interface DocumentManagerProps {
  transactionId: string;
  apiBaseUrl?: string;
}

const DOCUMENT_TYPE_LABELS: Record<string, string> = {
  PURCHASE_AGREEMENT: 'Purchase Agreement',
  PROOF_OF_FUNDS: 'Proof of Funds',
  CLOSING_DISCLOSURE: 'Closing Disclosure',
};

export default function DocumentManager({ transactionId, apiBaseUrl = 'http://localhost:3001/api/v1' }: DocumentManagerProps) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [processingDoc, setProcessingDoc] = useState<string | null>(null);
  const [validatingDoc, setValidatingDoc] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  /**
   * Generate all documents for the transaction
   */
  const handleGenerateDocuments = async () => {
    setIsGenerating(true);
    setError(null);

    try {
      const response = await fetch(`${apiBaseUrl}/transactions/${transactionId}/generate-documents`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) {
        throw new Error('Failed to generate documents');
      }

      const data = await response.json();
      setDocuments(data.documents || []);
    } catch (err: any) {
      setError(err.message || 'Failed to generate documents');
      console.error('Error generating documents:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  /**
   * Process a document with OCR
   */
  const handleProcessOCR = async (documentId: string) => {
    setProcessingDoc(documentId);
    setError(null);

    try {
      const response = await fetch(`${apiBaseUrl}/documents/${documentId}/process-ocr`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) {
        throw new Error('Failed to process OCR');
      }

      const data = await response.json();

      // Update document in list
      setDocuments((prev) =>
        prev.map((doc) =>
          doc.id === documentId
            ? {
                ...doc,
                extractedData: data.document.extractedData,
                pageCount: data.document.pageCount,
                status: 'PENDING_REVIEW',
              }
            : doc
        )
      );
    } catch (err: any) {
      setError(err.message || 'Failed to process OCR');
      console.error('Error processing OCR:', err);
    } finally {
      setProcessingDoc(null);
    }
  };

  /**
   * Validate a document
   */
  const handleValidate = async (documentId: string) => {
    setValidatingDoc(documentId);
    setError(null);

    try {
      const response = await fetch(`${apiBaseUrl}/documents/${documentId}/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) {
        throw new Error('Failed to validate document');
      }

      const data = await response.json();

      // Update document in list
      setDocuments((prev) =>
        prev.map((doc) =>
          doc.id === documentId
            ? {
                ...doc,
                validationPerformed: true,
                validationResults: data.validationResults,
                validationPassed: data.validationPassed,
                status: data.validationPassed ? 'APPROVED' : 'REJECTED',
              }
            : doc
        )
      );
    } catch (err: any) {
      setError(err.message || 'Failed to validate document');
      console.error('Error validating document:', err);
    } finally {
      setValidatingDoc(null);
    }
  };

  /**
   * Download a document
   */
  const handleDownload = (documentId: string, filename: string) => {
    const url = `${apiBaseUrl}/documents/${documentId}/download`;
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle>Document Generation & OCR Demo</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-600 mb-4">
            Generate realistic closing documents, process them with OCR, and validate extracted data.
            This demonstrates the complete document processing pipeline.
          </p>

          <Button
            onClick={handleGenerateDocuments}
            disabled={isGenerating}
            size="lg"
            className="w-full sm:w-auto"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Generating Documents...
              </>
            ) : (
              <>
                <PlayCircle className="w-4 h-4 mr-2" />
                Generate All Documents
              </>
            )}
          </Button>

          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              <strong>Error:</strong> {error}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Documents List */}
      {documents.length > 0 && (
        <div className="grid gap-4 md:grid-cols-1 lg:grid-cols-1">
          {documents.map((doc) => (
            <Card key={doc.id} className="border-2">
              <CardContent className="pt-6">
                <div className="space-y-4">
                  {/* Document Header */}
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                      <div className="p-2 bg-blue-100 rounded-lg">
                        <FileText className="w-6 h-6 text-blue-600" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-lg">
                          {DOCUMENT_TYPE_LABELS[doc.documentType] || doc.documentType}
                        </h3>
                        <p className="text-sm text-gray-600">{doc.filename}</p>
                        {doc.pageCount && (
                          <p className="text-xs text-gray-500">{doc.pageCount} page(s)</p>
                        )}
                      </div>
                    </div>

                    {/* Status Badge */}
                    <span
                      className={cn(
                        'px-3 py-1 rounded-full text-xs font-medium',
                        doc.status === 'APPROVED' && 'bg-green-100 text-green-700',
                        doc.status === 'REJECTED' && 'bg-red-100 text-red-700',
                        doc.status === 'PENDING_REVIEW' && 'bg-yellow-100 text-yellow-700',
                        doc.status === 'UPLOADED' && 'bg-blue-100 text-blue-700'
                      )}
                    >
                      {doc.status}
                    </span>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex flex-wrap gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleDownload(doc.id, doc.filename)}
                    >
                      <Download className="w-4 h-4 mr-1" />
                      Download PDF
                    </Button>

                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleProcessOCR(doc.id)}
                      disabled={processingDoc === doc.id || !!doc.extractedData}
                    >
                      {processingDoc === doc.id ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                          Processing...
                        </>
                      ) : (
                        <>
                          <ScanEye className="w-4 h-4 mr-1" />
                          {doc.extractedData ? 'OCR Complete' : 'Run OCR'}
                        </>
                      )}
                    </Button>

                    {doc.extractedData && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleValidate(doc.id)}
                        disabled={validatingDoc === doc.id || doc.validationPerformed}
                      >
                        {validatingDoc === doc.id ? (
                          <>
                            <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                            Validating...
                          </>
                        ) : (
                          <>
                            <CheckCircle className="w-4 h-4 mr-1" />
                            {doc.validationPerformed ? 'Validated' : 'Validate'}
                          </>
                        )}
                      </Button>
                    )}
                  </div>

                  {/* Extracted Data */}
                  {doc.extractedData && Object.keys(doc.extractedData).length > 0 && (
                    <div className="border-t pt-4">
                      <h4 className="font-semibold text-sm mb-2 flex items-center gap-2">
                        <ScanEye className="w-4 h-4 text-blue-600" />
                        Extracted Data (OCR Results)
                      </h4>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        {Object.entries(doc.extractedData).map(([key, value]) => (
                          <div key={key} className="bg-gray-50 p-2 rounded">
                            <span className="text-gray-600 text-xs">{key}:</span>
                            <p className="font-medium text-gray-900">
                              {value !== null && value !== undefined ? String(value) : 'N/A'}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Validation Results */}
                  {doc.validationResults && doc.validationResults.length > 0 && (
                    <div className="border-t pt-4">
                      <h4 className="font-semibold text-sm mb-3 flex items-center gap-2">
                        {doc.validationPassed ? (
                          <CheckCircle className="w-4 h-4 text-green-600" />
                        ) : (
                          <XCircle className="w-4 h-4 text-red-600" />
                        )}
                        Validation Results
                      </h4>
                      <div className="space-y-2">
                        {doc.validationResults.map((result, index) => (
                          <div
                            key={index}
                            className={cn(
                              'p-3 rounded-lg border-2',
                              result.passed
                                ? 'bg-green-50 border-green-200'
                                : 'bg-red-50 border-red-200'
                            )}
                          >
                            <div className="flex items-start gap-2">
                              {result.passed ? (
                                <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                              ) : (
                                <XCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                              )}
                              <div className="flex-1">
                                <p className="font-medium text-sm">{result.description}</p>
                                {!result.passed && (
                                  <div className="mt-1 text-xs space-y-1">
                                    <p>
                                      <span className="text-gray-600">Expected:</span>{' '}
                                      <span className="font-medium">{String(result.expected)}</span>
                                    </p>
                                    <p>
                                      <span className="text-gray-600">Found:</span>{' '}
                                      <span className="font-medium">{String(result.found)}</span>
                                    </p>
                                  </div>
                                )}
                                <span
                                  className={cn(
                                    'inline-block mt-1 px-2 py-0.5 rounded text-xs font-medium',
                                    result.severity === 'critical'
                                      ? 'bg-red-100 text-red-700'
                                      : 'bg-yellow-100 text-yellow-700'
                                  )}
                                >
                                  {result.severity}
                                </span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Empty State */}
      {documents.length === 0 && !isGenerating && (
        <Card>
          <CardContent className="py-12 text-center">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">
              No documents generated yet. Click the button above to generate documents.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
