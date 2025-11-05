import express from 'express';
import { prisma } from '../lib/prisma.js';
import { TaskStatus } from '@prisma/client';

const router = express.Router();

// GET /api/v1/tasks - List all tasks
router.get('/', async (req, res) => {
  try {
    const { transactionId, status, assignedTo } = req.query;

    const where: any = {};
    if (transactionId) where.transactionId = transactionId as string;
    if (status) where.status = status as TaskStatus;
    if (assignedTo) where.assignedTo = assignedTo as string;

    const tasks = await prisma.task.findMany({
      where,
      orderBy: {
        createdAt: 'asc',
      },
    });

    res.json(tasks);
  } catch (error) {
    console.error('Error fetching tasks:', error);
    res.status(500).json({ error: 'Failed to fetch tasks' });
  }
});

// GET /api/v1/tasks/:id - Get task by ID
router.get('/:id', async (req, res) => {
  try {
    const task = await prisma.task.findUnique({
      where: { id: req.params.id },
      include: {
        transaction: true,
      },
    });

    if (!task) {
      return res.status(404).json({ error: 'Task not found' });
    }

    res.json(task);
  } catch (error) {
    console.error('Error fetching task:', error);
    res.status(500).json({ error: 'Failed to fetch task' });
  }
});

// POST /api/v1/tasks - Create a new task
router.post('/', async (req, res) => {
  try {
    const {
      transactionId,
      title,
      description,
      taskType,
      assignedTo,
      assignedBy = 'system',
      priority = 'NORMAL',
      dueDate,
      isBlocking = false,
      relatedStage,
    } = req.body;

    // Generate task ID
    const year = new Date().getFullYear();
    const count = await prisma.task.count();
    const id = `TASK-${year}-${String(count + 1).padStart(4, '0')}`;

    const task = await prisma.task.create({
      data: {
        id,
        transactionId,
        title,
        description,
        taskType,
        assignedTo,
        assignedBy,
        priority,
        dueDate: dueDate ? new Date(dueDate) : undefined,
        isBlocking,
        relatedStage,
      },
    });

    res.status(201).json(task);
  } catch (error) {
    console.error('Error creating task:', error);
    res.status(500).json({ error: 'Failed to create task' });
  }
});

// POST /api/v1/tasks/:id/complete - Mark task as complete
router.post('/:id/complete', async (req, res) => {
  try {
    const { completedBy, completionNotes, completionData } = req.body;

    const task = await prisma.task.findUnique({
      where: { id: req.params.id },
    });

    if (!task) {
      return res.status(404).json({ error: 'Task not found' });
    }

    if (task.status === TaskStatus.COMPLETED) {
      return res.status(400).json({ error: 'Task is already completed' });
    }

    const updatedTask = await prisma.task.update({
      where: { id: req.params.id },
      data: {
        status: TaskStatus.COMPLETED,
        completedAt: new Date(),
        completedBy,
        completionNotes,
        completionData: completionData || {},
      },
    });

    res.json(updatedTask);
  } catch (error) {
    console.error('Error completing task:', error);
    res.status(500).json({ error: 'Failed to complete task' });
  }
});

// PATCH /api/v1/tasks/:id - Update task
router.patch('/:id', async (req, res) => {
  try {
    const updates = req.body;

    // Convert date strings to Date objects
    if (updates.dueDate) updates.dueDate = new Date(updates.dueDate);
    if (updates.startedAt) updates.startedAt = new Date(updates.startedAt);

    const task = await prisma.task.update({
      where: { id: req.params.id },
      data: updates,
    });

    res.json(task);
  } catch (error) {
    console.error('Error updating task:', error);
    res.status(500).json({ error: 'Failed to update task' });
  }
});

// DELETE /api/v1/tasks/:id - Delete task
router.delete('/:id', async (req, res) => {
  try {
    await prisma.task.delete({
      where: { id: req.params.id },
    });
    res.json({ message: 'Task deleted successfully' });
  } catch (error) {
    console.error('Error deleting task:', error);
    res.status(500).json({ error: 'Failed to delete task' });
  }
});

export default router;
