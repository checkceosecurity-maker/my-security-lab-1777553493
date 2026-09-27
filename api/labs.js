const { pool, ensureSchema, methodNotAllowed } = require('./_db')

module.exports = async function labs(req, res) {
  if (req.method !== 'GET') return methodNotAllowed(res, ['GET'])
  try { await ensureSchema(); const { rows } = await pool.query('SELECT id, slug, category, title, description, difficulty, created_at AS "createdAt" FROM security_labs ORDER BY id'); res.status(200).json({ data: rows }) } catch (error) { console.error('[v0] GET /api/labs failed', error); res.status(500).json({ error: 'Unable to load labs' }) }
}
module.exports.config = { maxDuration: 10 }
