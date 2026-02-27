import { useState, useEffect } from 'react'
import axios from 'axios'

export default function PlansTable() {
    const [plans, setPlans] = useState([])
    const [users, setUsers] = useState([]) // Справочник сотрудников
    const [showModal, setShowModal] = useState(false)
    const [isEditing, setIsEditing] = useState(false)

    const initialForm = { id: null, employee_id: '', date: '', status: 'Я' }
    const [formData, setFormData] = useState(initialForm)

    useEffect(() => {
        fetchData()
    }, [])

    const fetchData = async () => {
        try {
            const [usersRes, plansRes] = await Promise.all([
                axios.get('/api/users'),
                axios.get('/api/schedule-base')
            ])
            setUsers(usersRes.data)
            setPlans(plansRes.data)
        } catch (e) { console.error(e) }
    }

    // Хелпер для отображения имени вместо ID
    const getUserName = (id) => users.find(u => u.id === id)?.fio || `ID: ${id}`

    const openCreate = () => {
        setFormData({ ...initialForm, employee_id: users[0]?.id || '' })
        setIsEditing(false)
        setShowModal(true)
    }

    const openEdit = (plan) => {
        setFormData(plan)
        setIsEditing(true)
        setShowModal(true)
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        try {
            if (isEditing) {
                await axios.patch(`/api/schedule-base/${formData.id}`, formData)
            } else {
                await axios.post('/api/schedule-base', formData)
            }
            setShowModal(false)
            fetchData()
        } catch (e) {
            alert('Ошибка: ' + (e.response?.data?.error || e.message))
        }
    }

    const handleDelete = async (id) => {
        if (!confirm('Удалить запись плана?')) return
        await axios.delete(`/api/schedule-base/${id}`)
        fetchData()
    }

    return (
        <div>
            <button className="btn btn-success mb-3" onClick={openCreate}>+ Добавить запись в план</button>

            <table className="table table-hover align-middle">
                <thead className="table-light">
                    <tr>
                        <th>Дата</th>
                        <th>Сотрудник</th>
                        <th>Статус (Код)</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    {plans.map(p => (
                        <tr key={p.id}>
                            <td>{p.date}</td>
                            <td>{getUserName(p.employee_id)}</td>
                            <td>
                                <span className="badge bg-secondary">{p.status}</span>
                            </td>
                            <td>
                                <button className="btn btn-sm btn-outline-primary me-1" onClick={() => openEdit(p)}>Edit</button>
                                <button className="btn btn-sm btn-outline-danger" onClick={() => handleDelete(p.id)}>Delete</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>

            {showModal && (
                <div className="modal d-block" style={{background:'rgba(0,0,0,0.5)'}}>
                    <div className="modal-dialog">
                        <div className="modal-content">
                            <div className="modal-header">
                                <h5 className="modal-title">{isEditing ? 'Правка записи' : 'Новая запись'}</h5>
                                <button className="btn-close" onClick={()=>setShowModal(false)}></button>
                            </div>
                            <div className="modal-body">
                                <form onSubmit={handleSubmit}>
                                    <div className="mb-3">
                                        <label>Дата</label>
                                        <input type="date" className="form-control" required value={formData.date} onChange={e=>setFormData({...formData, date: e.target.value})} />
                                    </div>
                                    <div className="mb-3">
                                        <label>Сотрудник</label>
                                        <select className="form-select" required value={formData.employee_id} onChange={e=>setFormData({...formData, employee_id: parseInt(e.target.value)})}>
                                            <option value="" disabled>Выберите...</option>
                                            {users.map(u => <option key={u.id} value={u.id}>{u.fio}</option>)}
                                        </select>
                                    </div>
                                    <div className="mb-3">
                                        <label>Статус</label>
                                        <select className="form-select" value={formData.status} onChange={e=>setFormData({...formData, status: e.target.value})}>
                                            <option value="Я">Я (Работа)</option>
                                            <option value="Д">Д (Удаленно)</option>
                                            <option value="В">В (Выходной)</option>
                                            <option value="О">О (Отпуск)</option>
                                            <option value="Б">Б (Больничный)</option>
                                            <option value="К">К (Командировка)</option>
                                            <option value="ЯД">ЯД (До обеда в офисе)</option>
                                            <option value="ДЯ">ДЯ (После обеда в офисе)</option>
                                            <option value="У">У (Учебный отпуск)</option>
                                        </select>
                                    </div>
                                    <div className="text-end">
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