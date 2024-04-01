class DbRouter:
    app_labels = {'invmgmt': 'invmgmt_db', 'characteristics': 'characteristics_db'}

    def db_for_read(self, model, **hints):
        # print(f"** read {model}, {model._meta.app_label}")
        return self.app_labels.get(model._meta.app_label)

    def db_for_write(self, model, **hints):
        # print(f"** write {model}, {model._meta.app_label}")
        return self.app_labels.get(model._meta.app_label)

    def allow_relation(self, obj1, obj2, **hints):
        # only allow if moth models are in the same db
        return obj1._meta.app_label == obj2._meta.app_label

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # for now
        return True
