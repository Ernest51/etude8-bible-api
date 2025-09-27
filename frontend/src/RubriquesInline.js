import React from "react";

function RubriquesInline({ items, activeId, onSelect, rubriquesStatus }) {
  if (!items || items.length === 0) {
    return <div>Aucune rubrique disponible</div>;
  }

  const getLEDColor = (itemId) => {
    const status = rubriquesStatus[itemId];
    if (status === 'completed') return '#10b981'; // Vert
    if (status === 'in-progress') return '#f59e0b'; // Jaune  
    return '#9ca3af'; // Gris par défaut
  };

  return (
    <div className="rubriques-list">
      {items.map((item) => (
        <div
          key={item.id}
          className={`rubrique-item ${activeId === item.id ? 'active' : ''} ${
            rubriquesStatus[item.id] === 'completed' ? 'completed' : ''
          }`}
          onClick={() => onSelect && onSelect(item.id)}
        >
          <span className="rubrique-number">{item.id}</span>
          <span className="rubrique-title">{item.title}</span>
          
          {/* LED physique avec 3 états */}
          <div 
            className="rubrique-led"
            style={{
              width: '10px',
              height: '10px',
              borderRadius: '50%',
              backgroundColor: getLEDColor(item.id),
              border: '2px solid #fff',
              boxShadow: `0 0 4px ${getLEDColor(item.id)}`,
              marginLeft: 'auto',
              flexShrink: 0
            }}
            title={
              rubriquesStatus[item.id] === 'completed' ? 'Terminé' :
              rubriquesStatus[item.id] === 'in-progress' ? 'En cours' : 'Non commencé'
            }
          />
        </div>
      ))}
    </div>
  );
}

export default RubriquesInline;