import config
import signals

def main():
    print("Press enter to skip tests. Press any other key to run tests.")
    if input() == "":
        print("Skipping tests...")
    else:
        import tests
        print("\nRunning tests...\n")
        tests.run_tests()
        config.tested = True
    
    print("Now processing signals.")
        
    signals.main()
    
if __name__ == "__main__":
    main()