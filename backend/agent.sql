-- auto-generated definition
create table agent
(
    id           int unsigned auto_increment comment 'id'
        primary key,
    name         varchar(100) default ''                not null comment '智能体名称',
    photo        varchar(255) default ''                not null comment '头像',
    introduce    text                                   not null comment '介绍',
    role_setting text                                   not null comment '角色设定',
    prologue     text                                   not null comment '开场白',
    is_delete    tinyint(1)   default 2                 not null comment '是否删除1：删除 2：正常',
    user_id      int          default 0                 not null comment '创建用户id',
    create_time  timestamp    default CURRENT_TIMESTAMP not null comment '创建时间',
    update_time  timestamp    default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP comment '更新时间',
    agent_id     varchar(50)  default ''                not null comment '智能体id',
    temperature  float        default 0                 not null comment 'temperature'
)
    comment 'AI智能体';

create index idx_user_id
    on agent (user_id);



create table users
(
    id            int auto_increment comment '用户ID，主键'
        primary key,
    username      varchar(50)                           not null comment '用户名，唯一',
    email         varchar(100)                          not null comment '邮箱，唯一',
    password_hash varchar(255)                          not null comment '密码哈希值',
    full_name     varchar(100)                          null comment '用户全名',
    phone         varchar(20)                           null comment '手机号码',
    created_at    timestamp   default CURRENT_TIMESTAMP null comment '创建时间',
    updated_at    timestamp   default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP comment '更新时间',
    last_login    timestamp                             null comment '最后登录时间',
    is_active     tinyint(1)  default 1                 null comment '账户是否激活',
    role          varchar(20) default 'user'            null comment '用户角色：user-普通用户，admin-管理员',
    constraint email
        unique (email),
    constraint username
        unique (username)
)
    comment '用户信息表';

create index idx_email
    on users (email)
    comment '邮箱索引';

create index idx_username
    on users (username)
    comment '用户名索引';
