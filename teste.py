import multiprocessing
import pygame



def worker(shared_list, idx):
    # Access and modify the shared list
    shared_list.append("worker " + str(idx))

if __name__ == "__main__":
    print('test')
    
    # Create a manager object
    manager = multiprocessing.Manager()

    # Create a shared list using the manager
    shared_list = manager.list()

    # Create multiple worker processes
    num_threads = 4
    processes = []
    for _ in range(num_threads):
        p = multiprocessing.Process(target=worker, args=(shared_list, _))
        processes.append(p)
        p.start()

    # Wait for all processes to finish
    for p in processes:
        p.join()

    # Print the contents of the shared list
    print(shared_list)