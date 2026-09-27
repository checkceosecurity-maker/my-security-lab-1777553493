const { pool, ensureSchema, methodNotAllowed } = require('./_db')

module.exports = async function progress(req, res) {
  if (req.method !== 'POST') return methodNotAllowed(res, ['POST'])
  const { labId, completed = true, score = null } = req.body || {}
  if (!Number.isInteger(Number(labId)) || Number(labId) < 1) return res.status(400).json({ error: 'labId must be a positive integer' })
  if (score !== null && (!Number.isFinite(Number(score)) || Number(score) < 0 || Number(score) > 10)) return res.status(400).json({ error: 'score must be between 0 and 10' })
  try { await ensureSchema(); const { rows } = await pool.query('INSERT INTO learning_progress (lab_id, completed, score) VALUES ($1, $2, $3) ON CONFLICT (lab_id) DO UPDATE SET completed = EXCLUDED.completed, score = EXCLUDED.score, updated_at = NOW() RETURNING id, lab_id AS "labId", completed, score, updated_at AS "updatedAt"', [Number(labId), Boolean(completed), score === null ? null : Number(score)]); res.status(200).json({ data: rows[0] }) } catch (error) { console.error('[v0] POST /api/progress failed', error); res.status(500).json({ error: 'Unable to save progress' }) }
}
module.exports.config = { maxDuration: 10 }
