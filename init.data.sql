INSERT INTO public.institution (institution_id, name, acronym, lattes_id)
VALUES ('083a16f0-cccf-47d2-a676-d10b8931f66b', 'UNIVERSIDADE PADRÃO', 'UP', '000');

INSERT INTO roles (id, role)
VALUES ('2094ba5c-a5b3-4bcb-81e4-f5c323eab0ed','Manutenção');

INSERT INTO permission (role_id, permission)
VALUES ('2094ba5c-a5b3-4bcb-81e4-f5c323eab0ed','visualizar_modulo_administrativo'),
       ('2094ba5c-a5b3-4bcb-81e4-f5c323eab0ed', 'visualizar_gerencia_modulo_administrativo'), 
       ('2094ba5c-a5b3-4bcb-81e4-f5c323eab0ed', 'editar_cargos_permissoes'), 
       ('2094ba5c-a5b3-4bcb-81e4-f5c323eab0ed', 'editar_cargos_usuarios'), 
       ('2094ba5c-a5b3-4bcb-81e4-f5c323eab0ed', 'editar_informacoes_usuarios'),
       ('2094ba5c-a5b3-4bcb-81e4-f5c323eab0ed', 'editar_configuracoes_plataforma'),
       ('2094ba5c-a5b3-4bcb-81e4-f5c323eab0ed', 'atualizar_apache_hop'), 
       ('2094ba5c-a5b3-4bcb-81e4-f5c323eab0ed', 'visualizar_todos_departamentos'), 
       ('2094ba5c-a5b3-4bcb-81e4-f5c323eab0ed', 'visualizar_todos_programas'), 
       ('2094ba5c-a5b3-4bcb-81e4-f5c323eab0ed', 'editar_informacoes_programa'), 
       ('2094ba5c-a5b3-4bcb-81e4-f5c323eab0ed', 'editar_informacoes_departamento'), 
       ('2094ba5c-a5b3-4bcb-81e4-f5c323eab0ed', 'editar_docentes_programa'), 
       ('2094ba5c-a5b3-4bcb-81e4-f5c323eab0ed', 'editar_discentes_programa'), 
       ('2094ba5c-a5b3-4bcb-81e4-f5c323eab0ed', 'editar_docentes_departamento'), 
       ('2094ba5c-a5b3-4bcb-81e4-f5c323eab0ed', 'editar_tecnicos_departamento'), 
       ('2094ba5c-a5b3-4bcb-81e4-f5c323eab0ed', 'editar_pesos_avaliacao'), 
       ('2094ba5c-a5b3-4bcb-81e4-f5c323eab0ed', 'visualizar_indicadores_instituicao'), 
       ('2094ba5c-a5b3-4bcb-81e4-f5c323eab0ed', 'visualizar_grupos_pesquisa'),
       ('2094ba5c-a5b3-4bcb-81e4-f5c323eab0ed', 'visualizar_inct'), 
       ('2094ba5c-a5b3-4bcb-81e4-f5c323eab0ed', 'visualizar_indicadores_pos_graduacao'), 
       ('2094ba5c-a5b3-4bcb-81e4-f5c323eab0ed', 'adicionar_programa'), 
       ('2094ba5c-a5b3-4bcb-81e4-f5c323eab0ed', 'deletar_programa'), 
       ('2094ba5c-a5b3-4bcb-81e4-f5c323eab0ed', 'adicionar_departamento'), 
       ('2094ba5c-a5b3-4bcb-81e4-f5c323eab0ed', 'deletar_departamento'), 
       ('2094ba5c-a5b3-4bcb-81e4-f5c323eab0ed', 'criar_barema_avaliacao'), 
       ('2094ba5c-a5b3-4bcb-81e4-f5c323eab0ed', 'enviar_notificacoes'), 
       ('2094ba5c-a5b3-4bcb-81e4-f5c323eab0ed', 'editar_pesquisadores'), 
       ('2094ba5c-a5b3-4bcb-81e4-f5c323eab0ed', 'visualizar_pesquisadores'), 
       ('2094ba5c-a5b3-4bcb-81e4-f5c323eab0ed', 'visualizar_indices_pesquisador');
INSERT INTO users (user_id, display_name, email, uid, institution_id)
VALUES ('9b7c08e3-f14c-40d7-b445-d7b8167d9437', 'Usuário Padrão', 'user@user.com', 'default', '083a16f0-cccf-47d2-a676-d10b8931f66b' );
INSERT INTO users_roles (role_id, user_id)
VALUES ('2094ba5c-a5b3-4bcb-81e4-f5c323eab0ed', '9b7c08e3-f14c-40d7-b445-d7b8167d9437');