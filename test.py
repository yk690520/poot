

class test():
    @classmethod
    def __new__(cls, *args, **kwargs):

        if not hasattr(cls,'_instance'):
            cls._instance=super(test,cls).__new__(cls)

            return cls._instance

        return cls._instance



if __name__ == '__main__':
    t1=test()
    t2=test()
    print(t1==t2)