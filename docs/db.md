# Database

## Schema

### `task`

| Attribute   | Type                                     | Remark                     |
| ----------- | ---------------------------------------- | -------------------------- |
| id          | CHAR(36) PRIMARY KEY                     | Task ID (UUID)             |
| user_id     | CHAR(36) NOT NULL                        | User ID                    |
| status      | ENUM('pending','processing','done','failed') NOT NULL DEFAULT 'pending' | Task Status |
| created_at  | TIMESTAMP DEFAULT CURRENT_TIMESTAMP      | Create Time                |
| updated_at  | TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | Latest Update Time |
