import { useState, useEffect } from 'react'
import axios from 'axios'

export default function UsersTable() {
    const [users, setUsers] = useState([])
    const [showModal, setShowModal] = useState(false)
    const [isEditing, setIsEditing] = useState(false) // Режим редактирования

    // Начальное состояние формы
    const initialForm = {
        id: null,
        fio: '', team: '', tg_user_id: '',
        employee_type: 'OFFICE_FIXED', role: 'user', is_active: true,
        start_time: '09:00', end_time: '18:00',
        lunch_start: '13:00', lunch_duration: 60
    }
    const [formData, setFormData] = useState(initialForm)

    useEffect(() => { fetchUsers() }, [])

    const fetchUsers = async () => {
        try {
            const res = await axios.get('/api/users')
            setUsers(res.data)
        } catch (e) { console.error(e) }
    }

    const openCreate = () => {
        setFormData(initialForm)
        setIsEditing(false)
        setShowModal(true)
    }

    const openEdit = (user) => {
        setFormData({
            ...user,
            // Если tg_id null, превращаем в пустую строку для input
            tg_user_id: user.tg_user_id || ''
        })
        setIsEditing(true)
        setShowModal(true)
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        try {
            const payload = { ...formData, tg_user_id: formData.tg_user_id ? parseInt(formData.tg_user_id) : null }

            if (isEditing) {
                await axios.patch(`/api/users/${formData.id}`, payload)
            } else {
                await axios.post('/api/users', payload)
            }
            setShowModal(false)
            fetchUsers()
        } catch (e) {
            alert('Ошибка: ' + (e.response?.data?.error || e.message))
        }
    }

    const handleDelete = async (id) => {
        if (!confirm('Удалить сотрудника?')) return
        await axios.delete(`/api/users/${id}`)
        fetchUsers()
    }

    return (
        <div>
            <button className="btn btn-success mb-3" onClick={openCreate}>Добавить сотрудника</button>

            <div className="table-responsive">
                <table className="table table-sm table-hover align-middle">
                    <thead className="table-light">
                        <tr>
                            <th>ФИО</th>
                            <th>Отдел</th>
                            <th>TG ID</th>
                            <th>Тип</th>
                            <th>Роль</th>
                            <th>График</th>
                            <th>Статус</th>
                            <th>Действия</th>
                        </tr>
                    </thead>
                    <tbody>
                        {users.map(u => (
                            <tr key={u.id} className={!u.is_active ? 'table-secondary text-muted' : ''}>
                                <td>{u.fio}</td>
                                <td>{u.team}</td>
                                <td>{u.tg_user_id}</td>
                                <td><small>{u.employee_type}</small></td>
                                <td>{u.role}</td>
                                <td><small>{u.start_time}-{u.end_time}<br/>Обед: {u.lunch_start}</small></td>
                                <td>{u.is_active ? 'Активный' : 'Неактивный'}</td>
                                <td>
                                    <button className="btn btn-sm btn-outline-primary me-1" onClick={() => openEdit(u)}>Edit</button>
                                    <button className="btn btn-sm btn-outline-danger" onClick={() => handleDelete(u.id)}>Delete</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {showModal && (
                <div className="modal d-block" style={{background:'rgba(0,0,0,0.5)'}}>
                    <div className="modal-dialog modal-lg">
                        <div className="modal-content">
                            <div className="modal-header">
                                <h5 className="modal-title">{isEditing ? 'Редактирование' : 'Новый сотрудник'}</h5>
                                <button className="btn-close" onClick={() => setShowModal(false)}></button>
                            </div>
                            <div className="modal-body">
                                <form onSubmit={handleSubmit}>
                                    <div className="row g-3">
                                        <div className="col-md-6">
                                            <label>ФИО</label>
                                            <input className="form-control" required value={formData.fio} onChange={e=>setFormData({...formData, fio: e.target.value})}/>
                                        </div>
                                        <div className="col-md-6">
                                            <label>Отдел</label>
                                            <input className="form-control" required value={formData.team} onChange={e=>setFormData({...formData, team: e.target.value})}/>
                                        </div>
                                        <div className="col-md-4">
                                            <label>TG User ID</label>
                                            <input type="number" className="form-control" value={formData.tg_user_id} onChange={e=>setFormData({...formData, tg_user_id: e.target.value})}/>
                                        </div>
                                        <div className="col-md-4">
                                            <label>Тип</label>
                                            <select className="form-select" value={formData.employee_type} onChange={e=>setFormData({...formData, employee_type: e.target.value})}>
                                                <option value="OFFICE_FIXED">Офис 5/2</option>
                                                <option value="OFFICE_FLEX">Гибкий офис</option>
                                                <option value="ALWAYS_REMOTE">Удаленка</option>
                                                <option value="REMOTE_BY_SCHEDULE">Гибрид</option>
                                            </select>
                                        </div>
                                        <div className="col-md-4">
                                            <label>Роль</label>
                                            <select className="form-select" value={formData.role} onChange={e=>setFormData({...formData, role: e.target.value})}>
                                                <option value="user">User</option>
                                                <option value="admin">Admin</option>
                                            </select>
                                        </div>
                                        <div className="col-md-4">
                                            <label>Начало</label>
                                            <input type="time" className="form-control" value={formData.start_time} onChange={e=>setFormData({...formData, start_time: e.target.value})}/>
                                        </div>
                                        <div className="col-md-4">
                                            <label>Конец</label>
                                            <input type="time" className="form-control" value={formData.end_time} onChange={e=>setFormData({...formData, end_time: e.target.value})}/>
                                        </div>
                                        <div className="col-md-4">
                                            <label>Начало обеда</label>
                                            <input type="time" className="form-control" value={formData.lunch_start} onChange={e=>setFormData({...formData, lunch_start: e.target.value})}/>
                                        </div>
                                        <div className="col-12 form-check ms-2">
                                            <input type="checkbox" className="form-check-input" id="isActive" checked={formData.is_active} onChange={e=>setFormData({...formData, is_active: e.target.checked})}/>
                                            <label className="form-check-label" htmlFor="isActive">Активный сотрудник</label>
                                        </div>
                                    </div>
                                    <div className="mt-4 text-end">
                                        <button type="button" className="btn btn-secondary me-2" onClick={()=>setShowModal(false)}>Отмена</button>
                                        <button type="submit" className="btn btn-primary">Сохранить</button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}