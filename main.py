import ml.transformer as t

if __name__ == '__main__':
    t.prepare_transformer()
    print(t.make_prediction('{"key":"value"}'))
