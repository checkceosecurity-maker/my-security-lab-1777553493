const { pool, ensureSchema, methodNotAllowed } = require('./_db')

module.exports = async function dashboard(req, res) {
  if (req.method !== 'GET') return methodNotAllowed(res, ['GET'])
  try { await ensureSchema(); const { rows } = await pool.query(`SELECT COUNT(*)::int AS total, COUNT(*) FILTER (WHERE completed)::int AS completed, COALESCE(AVG(score) FILTER (WHERE score IS NOT NULL), 0)::numeric(5,2) AS average_score FROM learning_progress`); const stats = rows[0]; const total = Number(stats.total); const completed = Number(stats.completed); res.status(200).json({ data: { progress: total ? Math.round((completed / total) * 100) : 0, completedLabs: completed, securityScore: Number(stats.average_score), streakDays: 0 } }) } catch (error) { console.error('[v0] GET /api/dashboard failed', error); res.status(500).json({ error: 'Unable to load dashboard' }) }
}
module.exports.config = { maxDuration: 10 }
