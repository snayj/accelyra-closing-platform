import express from 'express';
import { prisma } from '../lib/prisma.js';
import { TransactionStage, EarnestMoneyStatus } from '@prisma/client';

const router = express.Router();

// GET /api/v1/transactions - List all transactions
router.get('/', async (req, res) => {
  try {
    const transactions = await prisma.transaction.findMany({
      include: {
        buyer: true,
        seller: true,
        buyerAgent: true,
        sellerAgent: true,
        loanOfficer: true,
        titleOfficer: true,
      },
      orderBy: {
        createdAt: 'desc',
      },
    });
    res.json(transactions);
  } catch (error) {
    console.error('Error fetching transactions:', error);
    res.status(500).json({ error: 'Failed to fetch transactions' });
  }
});

// GET /api/v1/transactions/:id - Get transaction by ID
router.get('/:id', async (req, res) => {
  try {
    const transaction = await prisma.transaction.findUnique({
      where: { id: req.params.id },
      include: {
        buyer: true,
        seller: true,
        buyerAgent: true,
        sellerAgent: true,
        loanOfficer: true,
        titleOfficer: true,
        tasks: {
          orderBy: {
            createdAt: 'asc',
          },
        },
        documents: {
          orderBy: {
            uploadedAt: 'desc',
          },
        },
      },
    });

    if (!transaction) {
      return res.status(404).json({ error: 'Transaction not found' });
    }

    res.json(transaction);
  } catch (error) {
    console.error('Error fetching transaction:', error);
    res.status(500).json({ error: 'Failed to fetch transaction' });
  }
});

// POST /api/v1/transactions - Create a new transaction
router.post('/', async (req, res) => {
  try {
    const {
      propertyAddress,
      propertyType,
      propertySqft,
      propertyBedrooms,
      propertyBathrooms,
      propertyYearBuilt,
      purchasePrice,
      downPayment,
      loanAmount,
      earnestMoneyAmount,
      buyerId,
      sellerId,
      buyerAgentId,
      sellerAgentId,
      loanOfficerId,
      titleOfficerId,
      priority,
      notes,
    } = req.body;

    // Generate transaction ID
    const year = new Date().getFullYear();
    const count = await prisma.transaction.count();
    const id = `TXN-${year}-${String(count + 1).padStart(4, '0')}`;

    // Calculate estimated closing date (13 days from now)
    const estimatedClosingDate = new Date();
    estimatedClosingDate.setDate(estimatedClosingDate.getDate() + 13);

    // Initialize stage history
    const stageHistory = [
      {
        stage: TransactionStage.OFFER_ACCEPTED,
        enteredAt: new Date().toISOString(),
        notes: 'Transaction created',
      },
    ];

    const transaction = await prisma.transaction.create({
      data: {
        id,
        propertyAddress,
        propertyType,
        propertySqft,
        propertyBedrooms,
        propertyBathrooms,
        propertyYearBuilt,
        purchasePrice,
        downPayment,
        loanAmount,
        earnestMoneyAmount,
        buyerId,
        sellerId,
        buyerAgentId,
        sellerAgentId,
        loanOfficerId,
        titleOfficerId,
        priority: priority || 'NORMAL',
        notes,
        currentStage: TransactionStage.OFFER_ACCEPTED,
        stageHistory: stageHistory as any,
        stageStartedAt: new Date(),
        estimatedClosingDate,
      },
      include: {
        buyer: true,
        seller: true,
        buyerAgent: true,
        sellerAgent: true,
      },
    });

    res.status(201).json(transaction);
  } catch (error) {
    console.error('Error creating transaction:', error);
    res.status(500).json({ error: 'Failed to create transaction' });
  }
});

// POST /api/v1/transactions/:id/advance-stage - Advance to next stage
router.post('/:id/advance-stage', async (req, res) => {
  try {
    const { force = false } = req.body;
    const transaction = await prisma.transaction.findUnique({
      where: { id: req.params.id },
      include: {
        tasks: true,
      },
    });

    if (!transaction) {
      return res.status(404).json({ error: 'Transaction not found' });
    }

    // Check if already at final stage
    if (transaction.currentStage === TransactionStage.RECORDING_COMPLETE) {
      return res.status(400).json({ error: 'Transaction is already at final stage' });
    }

    // Check for blocking tasks if not forced
    if (!force) {
      const blockingTasks = transaction.tasks.filter(
        (task) => task.isBlocking && task.status !== 'COMPLETED'
      );
      if (blockingTasks.length > 0) {
        return res.status(400).json({
          error: 'Cannot advance stage: blocking tasks not completed',
          blockingTasks: blockingTasks.map((t) => ({ id: t.id, title: t.title })),
        });
      }
    }

    // Determine next stage
    const stageOrder = [
      TransactionStage.OFFER_ACCEPTED,
      TransactionStage.TITLE_SEARCH,
      TransactionStage.UNDERWRITING,
      TransactionStage.CLEAR_TO_CLOSE,
      TransactionStage.FINAL_DOCUMENTS,
      TransactionStage.FUNDING_SIGNING,
      TransactionStage.RECORDING_COMPLETE,
    ];

    const currentIndex = stageOrder.indexOf(transaction.currentStage);
    const nextStage = stageOrder[currentIndex + 1];

    // Update stage history
    const stageHistory = transaction.stageHistory as any[];
    stageHistory.push({
      stage: nextStage,
      enteredAt: new Date().toISOString(),
      notes: req.body.notes || '',
    });

    // Update transaction
    const updatedTransaction = await prisma.transaction.update({
      where: { id: req.params.id },
      data: {
        currentStage: nextStage,
        stageHistory: stageHistory as any,
        stageStartedAt: new Date(),
        actualClosingDate: nextStage === TransactionStage.RECORDING_COMPLETE ? new Date() : undefined,
      },
      include: {
        buyer: true,
        seller: true,
        tasks: true,
      },
    });

    res.json(updatedTransaction);
  } catch (error) {
    console.error('Error advancing stage:', error);
    res.status(500).json({ error: 'Failed to advance stage' });
  }
});

// POST /api/v1/transactions/:id/deposit-earnest-money - Record earnest money deposit
router.post('/:id/deposit-earnest-money', async (req, res) => {
  try {
    const { amount } = req.body;
    const transaction = await prisma.transaction.findUnique({
      where: { id: req.params.id },
    });

    if (!transaction) {
      return res.status(404).json({ error: 'Transaction not found' });
    }

    // Update stage history
    const stageHistory = transaction.stageHistory as any[];
    stageHistory.push({
      stage: transaction.currentStage,
      enteredAt: new Date().toISOString(),
      event: 'earnest_money_deposited',
      amount,
    });

    const updatedTransaction = await prisma.transaction.update({
      where: { id: req.params.id },
      data: {
        earnestMoneyAmount: amount,
        earnestMoneyStatus: EarnestMoneyStatus.DEPOSITED,
        earnestMoneyDepositedAt: new Date(),
        stageHistory: stageHistory as any,
      },
    });

    res.json(updatedTransaction);
  } catch (error) {
    console.error('Error depositing earnest money:', error);
    res.status(500).json({ error: 'Failed to deposit earnest money' });
  }
});

// POST /api/v1/transactions/:id/verify-funds - Verify buyer funds
router.post('/:id/verify-funds', async (req, res) => {
  try {
    const { method = 'manual' } = req.body;
    const transaction = await prisma.transaction.findUnique({
      where: { id: req.params.id },
    });

    if (!transaction) {
      return res.status(404).json({ error: 'Transaction not found' });
    }

    // Update stage history
    const stageHistory = transaction.stageHistory as any[];
    stageHistory.push({
      stage: transaction.currentStage,
      enteredAt: new Date().toISOString(),
      event: 'funds_verified',
      method,
    });

    const updatedTransaction = await prisma.transaction.update({
      where: { id: req.params.id },
      data: {
        fundsVerified: true,
        fundsVerifiedAt: new Date(),
        fundsVerifiedBy: method,
        stageHistory: stageHistory as any,
      },
    });

    res.json(updatedTransaction);
  } catch (error) {
    console.error('Error verifying funds:', error);
    res.status(500).json({ error: 'Failed to verify funds' });
  }
});

// DELETE /api/v1/transactions/:id - Delete transaction
router.delete('/:id', async (req, res) => {
  try {
    await prisma.transaction.delete({
      where: { id: req.params.id },
    });
    res.json({ message: 'Transaction deleted successfully' });
  } catch (error) {
    console.error('Error deleting transaction:', error);
    res.status(500).json({ error: 'Failed to delete transaction' });
  }
});

// GET /api/v1/transactions/:id/progress - Get transaction progress
router.get('/:id/progress', async (req, res) => {
  try {
    const transaction = await prisma.transaction.findUnique({
      where: { id: req.params.id },
      include: {
        tasks: true,
      },
    });

    if (!transaction) {
      return res.status(404).json({ error: 'Transaction not found' });
    }

    const stageOrder = [
      'OFFER_ACCEPTED',
      'TITLE_SEARCH',
      'UNDERWRITING',
      'CLEAR_TO_CLOSE',
      'FINAL_DOCUMENTS',
      'FUNDING_SIGNING',
      'RECORDING_COMPLETE',
    ];

    const currentStageIndex = stageOrder.indexOf(transaction.currentStage);
    const progress = ((currentStageIndex + 1) / stageOrder.length) * 100;

    const totalTasks = transaction.tasks.length;
    const completedTasks = transaction.tasks.filter((t) => t.status === 'COMPLETED').length;
    const taskProgress = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;

    res.json({
      currentStage: transaction.currentStage,
      stageProgress: Math.round(progress),
      stageIndex: currentStageIndex + 1,
      totalStages: stageOrder.length,
      totalTasks,
      completedTasks,
      taskProgress: Math.round(taskProgress),
      estimatedClosingDate: transaction.estimatedClosingDate,
      actualClosingDate: transaction.actualClosingDate,
    });
  } catch (error) {
    console.error('Error fetching progress:', error);
    res.status(500).json({ error: 'Failed to fetch progress' });
  }
});

export default router;
