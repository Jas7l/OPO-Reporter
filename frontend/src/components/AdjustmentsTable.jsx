import { useState, useEffect } from 'react'
import axios from 'axios'

export default function AdjustmentsTable() {
    const [adjustments, setAdjustments] = useState([])
    const [users, setUsers] = useState([])
    const [showModal, setShowModal] = useState(false)
    const [isEditing, setIsEditing] = useState(false)

    // Форма с вложенным массивом absences
    const initialForm = {
        id: null, employee_id: '', date: '',
        status_override: '',
        start_time_override: '', end_time_override: '', lunch_start_override: '',
        absences: [] // Массив [{from, to, comment}]
    }
    const [formData, setFormData] = useState(initialForm)

    // Временные поля для добавления новой отлучки в список
    const [newAbsence, setNewAbsence] = useState({ from: '', to: '', comment: '' })

    useEffect(() => { fetchData() }, [])

    const fetchData = async () => {
        try {
            const [uRes, aRes] = await Promise.all([
                axios.get('/api/users'),
                axios.get('/api/schedule-adjustments')
            ])
            setUsers(uRes.data)
            setAdjustments(aRes.data)
        } catch (e) { console.error(e) }
    }

    const getUserName = (id) => users.find(u => u.id === id)?.fio || `ID: ${id}`

    const openCreate = () => {
        setFormData({ ...initialForm, employee_id: users[0]?.id || '' })
        setNewAbsence({ from: '', to: '', comment: '' })
        setIsEditing(false)
        setShowModal(true)
    }

    const openEdit = (adj) => {
        // если поля null, ставим пустые строки для input
        setFormData({
            ...adj,
            status_override: adj.status_override || '',
            start_time_override: adj.start_time_override || '',
            end_time_override: adj.end_time_override || '',
            lunch_start_override: adj.lunch_start_override || '',
            absences: adj.absences || [] // Если null, то пустой массив
        })
        setNewAbsence({ from: '', to: '', comment: '' })
        setIsEditing(true)
        setShowModal(true)
    }

    // Добавление отлучки в локальный массив формы
    const addAbsence = () => {
        if (!newAbsence.from || !newAbsence.to) return alert('Заполните время')
        setFormData({
            ...formData,
            absences: [...formData.absences, { ...newAbsence }]
        })
        setNewAbsence({ from: '', to: '', comment: '' })
    }

    // Удаление отлучки из локального массива
    const removeAbsence = (index) => {
        const updated = formData.absences.filter((_, i) => i !== index)
        setFormData({ ...formData, absences: updated })
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        try {
            // Очищаем пустые строки перед отправкой
            const payload = {
                ...formData,
                status_override: formData.status_override || null,
                start_time_override: formData.start_time_override || null,
                end_time_override: formData.end_time_override || null,
                lunch_start_override: formData.lunch_start_override || null,
                absences: formData.absences.length > 0 ? formData.absences : null
            }

            if (isEditing) {
                await axios.patch(`/api/schedule-adjustments/${formData.id}`, payload)
            } else {
                await axios.post('/api/schedule-adjustments', payload)
            }
            setShowModal(false)
            fetchData()
        } catch (e) {
            alert('Ошибка: ' + (e.response?.data?.error || e.message))
        }
    }

    const handleDelete = async (id) => {
        if (!confirm('Удалить правку?')) return
        await axios.delete(`/api/schedule-adjustments/${id}`)
        fetchData()
    }

    return (
        <div>
            <button className="btn btn-success mb-3" onClick={openCreate}>+ Добавить правку</button>

            <table className="table table-hover align-middle">
                <thead className="table-light">
                    <tr>
                        <th>Дата</th>
                        <th>Сотрудник</th>
                        <th>Смена статуса</th>
                        <th>Смена времени</th>
                        <th>Отлучки</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    {adjustments.map(a => (
                        <tr key={a.id}>
                            <td>{a.date}</td>
                            <td>{getUserName(a.employee_id)}</td>
                            <td>
                                {a.status_override ? <span className="badge bg-warning text-dark">{a.status_override}</span> : <span className="text-muted">-</span>}
                            </td>
                            <td>
                                {(a.start_time_override || a.end_time_override)
                                    ? <small>{a.start_time_override} - {a.end_time_override}</small>
                                    : <span className="text-muted">-</span>}
                            </td>
                            <td>
                                {a.absences && a.absences.length > 0
                                    ? <span className="badge bg-success">{a.absences.length} шт.</span>
                                    : <span className="text-muted">-</span>}
                            </td>
                            <td>
                                <button className="btn btn-sm btn-outline-primary me-1" onClick={() => openEdit(a)}>Edit</button>
                                <button className="btn btn-sm btn-outline-danger" onClick={() => handleDelete(a.id)}>Delete</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>

            {showModal && (
                <div className="modal d-block" style={{background:'rgba(0,0,0,0.5)', overflowY: 'auto'}}>
                    <div className="modal-dialog modal-lg">
                        <div className="modal-content">
                            <div className="modal-header">
                                <h5 className="modal-title">{isEditing ? 'Редактирование правки' : 'Новая правка'}</h5>
                                <button className="btn-close" onClick={()=>setShowModal(false)}></button>
                            </div>
                            <div className="modal-body">
                                <form onSubmit={handleSubmit}>
                                    <div className="row g-3">
                                        <div className="col-md-6">
                                            <label>Дата</label>
                                            <input type="date" className="form-control" required value={formData.date} onChange={e=>setFormData({...formData, date: e.target.value})} />
                                        </div>
                                        <div className="col-md-6">
                                            <label>Сотрудник</label>
                                            <select className="form-select" required value={formData.employee_id} onChange={e=>setFormData({...formData, employee_id: parseInt(e.target.value)})}>
                                                <option value="" disabled>Выберите...</option>
                                                {users.map(u => <option key={u.id} value={u.id}>{u.fio}</option>)}
                                            </select>
                                        </div>

                                        <div className="col-12"><hr/></div>

                                        <div className="col-md-3">
                                            <label>Смена статуса</label>
                                            <select className="form-select" value={formData.status_override} onChange={e=>setFormData({...formData, status_override: e.target.value})}>
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
                                        <div className="col-md-3">
                                            <label>Новое начало</label>
                                            <input type="time" className="form-control" value={formData.start_time_override} onChange={e=>setFormData({...formData, start_time_override: e.target.value})}/>
                                        </div>
                                        <div className="col-md-3">
                                            <label>Новый конец</label>
                                            <input type="time" className="form-control" value={formData.end_time_override} onChange={e=>setFormData({...formData, end_time_override: e.target.value})}/>
                                        </div>
                                        <div className="col-md-3">
                                            <label>Новый обед</label>
                                            <input type="time" className="form-control" value={formData.lunch_start_override} onChange={e=>setFormData({...formData, lunch_start_override: e.target.value})}/>
                                        </div>

                                        <div className="col-12"><hr/><h6>Отлучки (Absences)</h6></div>

                                        {/* Список добавленных отлучек */}
                                        <div className="col-12">
                                            {formData.absences.map((abs, idx) => (
                                                <div key={idx} className="alert alert-secondary d-flex justify-content-between py-1 px-2 mb-1">
                                                    <small>{abs.from} - {abs.to} ({abs.comment})</small>
                                                    <button type="button" className="btn-close btn-sm" onClick={() => removeAbsence(idx)}></button>
                                                </div>
                                            ))}
                                        </div>

                                        {/* Форма добавления отлучки */}
                                        <div className="col-md-3">
                                            <input type="time" className="form-control form-control-sm" placeholder="С" value={newAbsence.from} onChange={e=>setNewAbsence({...newAbsence, from: e.target.value})}/>
                                        </div>
                                        <div className="col-md-3">
                                            <input type="time" className="form-control form-control-sm" placeholder="По" value={newAbsence.to} onChange={e=>setNewAbsence({...newAbsence, to: e.target.value})}/>
                                        </div>
                                        <div className="col-md-4">
                                            <input type="text" className="form-control form-control-sm" placeholder="Комментарий" value={newAbsence.comment} onChange={e=>setNewAbsence({...newAbsence, comment: e.target.value})}/>
                                        </div>
                                        <div className="col-md-2">
                                            <button type="button" className="btn btn-sm btn-outline-success w-100" onClick={addAbsence}>Добавить</button>
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