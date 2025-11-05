import express from 'express';
import { prisma } from '../lib/prisma.js';
import { PartyRole } from '@prisma/client';

const router = express.Router();

// GET /api/v1/parties - List all parties
router.get('/', async (req, res) => {
  try {
    const { role } = req.query;

    const where: any = {};
    if (role) where.role = role as PartyRole;

    const parties = await prisma.party.findMany({
      where,
      orderBy: {
        name: 'asc',
      },
    });

    res.json(parties);
  } catch (error) {
    console.error('Error fetching parties:', error);
    res.status(500).json({ error: 'Failed to fetch parties' });
  }
});

// GET /api/v1/parties/:id - Get party by ID
router.get('/:id', async (req, res) => {
  try {
    const party = await prisma.party.findUnique({
      where: { id: req.params.id },
      include: {
        buyerTransactions: true,
        sellerTransactions: true,
        buyerAgentTransactions: true,
        sellerAgentTransactions: true,
      },
    });

    if (!party) {
      return res.status(404).json({ error: 'Party not found' });
    }

    res.json(party);
  } catch (error) {
    console.error('Error fetching party:', error);
    res.status(500).json({ error: 'Failed to fetch party' });
  }
});

// POST /api/v1/parties - Create a new party
router.post('/', async (req, res) => {
  try {
    const {
      name,
      email,
      phone,
      role,
      company,
      licenseNumber,
      address,
      city,
      state,
      zipCode,
      notes,
    } = req.body;

    // Generate party ID
    const count = await prisma.party.count();
    const id = `PARTY-${String(count + 1).padStart(3, '0')}`;

    const party = await prisma.party.create({
      data: {
        id,
        name,
        email,
        phone,
        role,
        company,
        licenseNumber,
        address,
        city,
        state,
        zipCode,
        notes,
      },
    });

    res.status(201).json(party);
  } catch (error) {
    console.error('Error creating party:', error);
    res.status(500).json({ error: 'Failed to create party' });
  }
});

// PATCH /api/v1/parties/:id - Update party
router.patch('/:id', async (req, res) => {
  try {
    const updates = req.body;

    const party = await prisma.party.update({
      where: { id: req.params.id },
      data: updates,
    });

    res.json(party);
  } catch (error) {
    console.error('Error updating party:', error);
    res.status(500).json({ error: 'Failed to update party' });
  }
});

// DELETE /api/v1/parties/:id - Delete party
router.delete('/:id', async (req, res) => {
  try {
    await prisma.party.delete({
      where: { id: req.params.id },
    });
    res.json({ message: 'Party deleted successfully' });
  } catch (error) {
    console.error('Error deleting party:', error);
    res.status(500).json({ error: 'Failed to delete party' });
  }
});

export default router;
