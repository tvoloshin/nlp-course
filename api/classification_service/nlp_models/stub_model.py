class StubModel:

    def predict(self, text: str) -> (str, float):
        return "stub_label", .99
