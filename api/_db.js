const { Pool } = require('pg')

const connectionString = process.env.DATABASE_URL || (process.env.POSTGRES_HOST && `postgresql://${encodeURIComponent(process.env.POSTGRES_USER || '')}:${encodeURIComponent(process.env.POSTGRES_PASSWORD || '')}@${process.env.POSTGRES_HOST}:${process.env.POSTGRES_PORT || 5432}/${process.env.POSTGRES_DB || 'postgres'}`)
if (!connectionString) throw new Error('DATABASE_URL or POSTGRES_HOST is required')

const pool = globalThis.__securityLabPool || new Pool({ connectionString, max: 5, idleTimeoutMillis: 10000, connectionTimeoutMillis: 5000, ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : undefined })
globalThis.__securityLabPool = pool

async function ensureSchema() {
  await pool.query('CREATE TABLE IF NOT EXISTS security_labs (id SERIAL PRIMARY KEY, slug TEXT UNIQUE NOT NULL, category TEXT NOT NULL, title TEXT NOT NULL, description TEXT NOT NULL, difficulty TEXT NOT NULL DEFAULT \'beginner\', created_at TIMESTAMPTZ NOT NULL DEFAULT NOW())')
  await pool.query('CREATE TABLE IF NOT EXISTS learning_progress (id SERIAL PRIMARY KEY, lab_id INTEGER NOT NULL REFERENCES security_labs(id) ON DELETE CASCADE, completed BOOLEAN NOT NULL DEFAULT FALSE, score NUMERIC(5,2), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), UNIQUE(lab_id))')
  await pool.query(`INSERT INTO security_labs (slug, category, title, description, difficulty) VALUES ('network-traffic-basics','Network','วิเคราะห์ทราฟฟิกเบื้องต้น','ฝึกอ่านแพ็กเก็ตและแยกสัญญาณผิดปกติจากทราฟฟิกปกติในสภาพแวดล้อมจำลอง','beginner'), ('web-api-defense','Web Security','ป้องกันช่องโหว่ Web API','เรียนรู้การตรวจสอบอินพุต การกำหนดสิทธิ์ และแนวทางป้องกัน endpoint ที่สำคัญ','intermediate'), ('incident-playbook','Blue Team','สร้าง Incident Playbook','ออกแบบขั้นตอนรับมือเหตุการณ์ ตั้งแต่ตรวจพบ แจ้งเตือน กักกัน จนถึงการฟื้นฟูระบบ','intermediate') ON CONFLICT (slug) DO NOTHING`)
}

function methodNotAllowed(res, allowed) { return res.status(405).setHeader('Allow', allowed.join(', ')).json({ error: 'Method not allowed' }) }
module.exports = { pool, ensureSchema, methodNotAllowed }
