-- disable macro_clic payment provider
UPDATE payment_provider
   SET macro_clic_commerce_id = NULL,
       macro_clic_secret_key = NULL,
       macro_clic_phrase = NULL,
       macro_clic_branch_id = NULL,
       macro_clic_ente_code = NULL;