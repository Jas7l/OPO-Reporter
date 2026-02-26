import { useState } from 'react'
import UsersTable from './components/UsersTable'
import PlansTable from './components/PlansTable'
import AdjustmentsTable from './components/AdjustmentsTable'

function App() {
  const [activeTab, setActiveTab] = useState('users')

  const tabs = [
    { id: 'users', label: 'Сотрудники'},
    { id: 'plans', label: 'Плановый график'},
    { id: 'adjustments', label: 'Ручные правки' },
  ]

  return (
    <div className="main-container container">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h3 className="fw-bold m-0">OPO Panel</h3>
            <p className="text-muted m-0 small">Система управления отчетностью</p>
        </div>
      </div>

      <div className="card">
        <div className="card-header bg-white pb-0 border-0 pt-4 px-4">
            <ul className="nav nav-pills mb-3">
                {tabs.map(tab => (
                    <li className="nav-item" key={tab.id}>
                        <button
                            className={`nav-link ${activeTab === tab.id ? 'active' : ''}`}
                            onClick={() => setActiveTab(tab.id)}
                        >
                            {tab.label}
                        </button>
                    </li>
                ))}
            </ul>
        </div>

        <div className="card-body px-4 pb-4">
          {activeTab === 'users' && <UsersTable />}
          {activeTab === 'plans' && <PlansTable />}
          {activeTab === 'adjustments' && <AdjustmentsTable />}
        </div>
      </div>
    </div>
  )
}

export default App