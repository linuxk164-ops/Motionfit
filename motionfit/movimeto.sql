CREATE TABLE movimento (
    id SERIAL PRIMARY KEY,
    motion_id INT NOT NULL REFERENCES motion(id) ON DELETE CASCADE,
    from_state_id INT NOT NULL REFERENCES motion_state(id) ON DELETE CASCADE,
    to_state_id INT NOT NULL REFERENCES motion_state(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

create index idx_movimento_motion_id on movimento(motion_id);
create index idx_movimento_from_state_id on movimento(from_state_id);
create index idx_movimento_to_state_id on movimento(to_state_id);

create TABLE movimento_history (
    id SERIAL PRIMARY KEY,
    movimento_id INT NOT NULL REFERENCES movimento(id) ON DELETE CASCADE,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by INT NOT NULL REFERENCES users(id) ON DELETE SET NULL
);

create index idx_movimento_history_movimento_id on movimento_history(movimento_id);
create index idx_movimento_history_changed_by on movimento_history(changed_by);
create index idx_movimento_history_changed_at on movimento_history(changed_at);

CREATE TABLE movimento_evolucao (
    id SERIAL PRIMARY KEY,
    movimento_id INT NOT NULL REFERENCES movimento(id) ON DELETE CASCADE,
    comment TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INT NOT NULL REFERENCES users(id) ON DELETE SET NULL
);

create index idx_movimento_evolucao_movimento_id on movimento_evolucao(movimento_id);
create index idx_movimento_evolucao_created_by on movimento_evolucao(created_by);
create index idx_movimento_evolucao_created_at on movimento_evolucao(created_at);