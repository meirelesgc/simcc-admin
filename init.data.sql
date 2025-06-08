INSERT INTO public.institution (institution_id, name, acronym, lattes_id)
VALUES ('083a16f0-cccf-47d2-a676-d10b8931f66b', 'UNIVERSIDADE PADRÃO', 'UP', '000');

INSERT INTO roles (id, role)
VALUES ('e40fc57d-d6a7-457f-994d-b0d0b3693b09','Manutenção');

INSERT INTO permission (role_id, permission)
VALUES ('e40fc57d-d6a7-457f-994d-b0d0b3693b09','visualizar_modulo_administrativo'),
       ('e40fc57d-d6a7-457f-994d-b0d0b3693b09', 'visualizar_gerencia_modulo_administrativo'), 
       ('e40fc57d-d6a7-457f-994d-b0d0b3693b09', 'editar_cargos_permissoes'), 
       ('e40fc57d-d6a7-457f-994d-b0d0b3693b09', 'editar_cargos_usuarios'), 
       ('e40fc57d-d6a7-457f-994d-b0d0b3693b09', 'editar_informacoes_usuarios'),
       ('e40fc57d-d6a7-457f-994d-b0d0b3693b09', 'editar_configuracoes_plataforma'),
       ('e40fc57d-d6a7-457f-994d-b0d0b3693b09', 'atualizar_apache_hop'), 
       ('e40fc57d-d6a7-457f-994d-b0d0b3693b09', 'visualizar_todos_departamentos'), 
       ('e40fc57d-d6a7-457f-994d-b0d0b3693b09', 'visualizar_todos_programas'), 
       ('e40fc57d-d6a7-457f-994d-b0d0b3693b09', 'editar_informacoes_programa'), 
       ('e40fc57d-d6a7-457f-994d-b0d0b3693b09', 'editar_informacoes_departamento'), 
       ('e40fc57d-d6a7-457f-994d-b0d0b3693b09', 'editar_docentes_programa'), 
       ('e40fc57d-d6a7-457f-994d-b0d0b3693b09', 'editar_discentes_programa'), 
       ('e40fc57d-d6a7-457f-994d-b0d0b3693b09', 'editar_docentes_departamento'), 
       ('e40fc57d-d6a7-457f-994d-b0d0b3693b09', 'editar_tecnicos_departamento'), 
       ('e40fc57d-d6a7-457f-994d-b0d0b3693b09', 'editar_pesos_avaliacao'), 
       ('e40fc57d-d6a7-457f-994d-b0d0b3693b09', 'visualizar_indicadores_instituicao'), 
       ('e40fc57d-d6a7-457f-994d-b0d0b3693b09', 'visualizar_grupos_pesquisa'),
       ('e40fc57d-d6a7-457f-994d-b0d0b3693b09', 'visualizar_inct'), 
       ('e40fc57d-d6a7-457f-994d-b0d0b3693b09', 'visualizar_indicadores_pos_graduacao'), 
       ('e40fc57d-d6a7-457f-994d-b0d0b3693b09', 'adicionar_programa'), 
       ('e40fc57d-d6a7-457f-994d-b0d0b3693b09', 'deletar_programa'), 
       ('e40fc57d-d6a7-457f-994d-b0d0b3693b09', 'adicionar_departamento'), 
       ('e40fc57d-d6a7-457f-994d-b0d0b3693b09', 'deletar_departamento'), 
       ('e40fc57d-d6a7-457f-994d-b0d0b3693b09', 'criar_barema_avaliacao'), 
       ('e40fc57d-d6a7-457f-994d-b0d0b3693b09', 'enviar_notificacoes'), 
       ('e40fc57d-d6a7-457f-994d-b0d0b3693b09', 'editar_pesquisadores'), 
       ('e40fc57d-d6a7-457f-994d-b0d0b3693b09', 'visualizar_pesquisadores'), 
       ('e40fc57d-d6a7-457f-994d-b0d0b3693b09', 'visualizar_indices_pesquisador');

INSERT INTO users (user_id, display_name, email, uid, institution_id)
VALUES ('9b7c08e3-f14c-40d7-b445-d7b8167d9437', 'Usuário Padrão', 'user@user.com', 'default', '083a16f0-cccf-47d2-a676-d10b8931f66b' );

INSERT INTO users_roles (role_id, user_id)
VALUES ('e40fc57d-d6a7-457f-994d-b0d0b3693b09', '9b7c08e3-f14c-40d7-b445-d7b8167d9437');