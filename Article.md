# Leveraging the power of cloud for distributed password cracking

[Passware](https://www.passware.com/), the leading provider of decryption software, has been offering a cloud integration for over a year now. Despite that, there is still close to no public knowledge about the specific challenges one might encounter during the deployment of cloud agents. This post aims to shine some light onto the process.

The 3 main questions I’ll try to answer, are:
1) What hardware configuration should you use?
2) How much is it going to cost you?
3) What are the privacy implications of using cloud agents?

Skip to the end of the article for key takeaways. For technical details, keep reading.

## What hardware configuration should you use?

[AWS EC2](https://aws.amazon.com/ec2/) is currently the only cloud platform officially supported by Passware, so we’ll ignore Microsoft’s and Google’s cloud offerings for now.

Additionally, this post will focus on GPU-accelerated password cracking. If your decryption needs involve mainly CPU-only algorithms, you should make different choices when selecting the instance type. You can check Passware’s GPU file type support on [this page](https://www.passware.com/kit-forensic/filetypes/). The general lessons from the rest of the article should still be relevant to you.

 

When it comes to GPU-accelerated computing, Amazon offers two distinct instance families: the P-series, which is labelled as a general purpose GPU instance, and the G-series, which is intended for machine learning inference and graphics-intensive workloads. There are usually several different configurations in each instance family, mainly differing in the number of CPU cores, RAM and GPU counts. Since the number of CPU cores and RAM are irrelevant for our application, and the price of multi-GPU systems increases more than linearly with every added GPU, we’ll stick with the basic single-GPU configuration of each family.

Referencing the useful Instance Types page, we can see which GPUs are used in each family:

![Table describing which GPU is used in which instance family](https://github.com/jankais3r/AWS-EC2-Price-Scraper/blob/master/Article_Images/1.png)

Passware has a [knowledge base article](https://support.passware.com/hc/en-us/articles/115000407228-What-are-system-and-GPU-recommendations-for-Passware-Kit-) intended to assist you with picking the right GPU, but in its current form it is rather incomplete and outdated, and it only mentions a general recommendation that more CUDA cores are better. Since all the offered GPUs are in the higher-priced workstation category, they are not as popular with the password cracking community as, let’s say, the gaming-focused RTX 2080 Ti. Because of that, there is not much information about their password cracking performance.

I spun up all of the instances and I ran a password recovery process on an MS Word 2019 file to benchmark the cards. These are the results (p/s = passwords per second):

![Table showing the performance of each instance type](https://github.com/jankais3r/AWS-EC2-Price-Scraper/blob/master/Article_Images/2.png)

What we’ve learned is that Tesla V100 provides roughly an equivalent performance to RTX 2080 Ti, while you would need three Tesla T4s to reach the same rate. It also demonstrated how insignificant the CPU choice is for GPU-optimized password cracking.

 
## How much is it going to cost you?

When it comes to pricing complexity, things are not much better here. More specifically, each instance type can run either Windows or Linux ([both are supported](https://support.passware.com/hc/en-us/articles/360022319153-Connecting-Passware-Kit-Agent-for-Amazon-EC2) by Passware) and each of those has a different price in each region. On top of that, those prices change over time.

Here is a price snapshot of a Windows-based p3.2xlarge instance on March 9, 2020:

![Table showing prices of the same instance type in different regions](https://github.com/jankais3r/AWS-EC2-Price-Scraper/blob/master/Article_Images/3.png)

As you can see, the price differences between regions are not negligible. What you need to consider when choosing the right region, however, is not only the price, but also the data privacy regulations in your region. More on that in the final section.

Now that we have an idea about prices, let’s revisit the performance table from earlier:

![Table comparing price per peformance of each instance type](https://github.com/jankais3r/AWS-EC2-Price-Scraper/blob/master/Article_Images/4.png)

When we consider both price and performance, suddenly the bang for buck winner is the g4dn.xlarge instance. This is likely to change when Amazon introduces new generation of instances, or when they adjust the prices of older generations to more closely match their performance.

To put things into perspective, if you wanted to double the performance of a machine with a single RTX 2080 Ti card (which costs around $1,100 as of this writing), you would need to spin up three g4dn.xlarge instances, running you around $60 per day.

Extrapolating from that, every 3 weeks of running those 3 instances would generate an AWS bill as high as it would cost you to buy an additional RTX 2080 Ti. While this is generally true of any cloud offering (that renting is more expensive than buying), cloud provides the benefit of scalability and no upfront investment. If you have an urgent job to finish, you can spin up a hundred of cloud instances and stop paying for them the next day after your passwords have been cracked. Billing per hour (in fact, AWS bills per second) also provides a simple re-charging model and allows you to transparently pass the costs onto a client if they request faster decryption and they accept the corresponding technology fees.

To simplify the process of finding the most efficient instance to use, I’ve written a script that pulls up-to-date prices from AWS marketplace and calculates which instance and region is currently the cheapest. You can get it [here](https://github.com/jankais3r/AWS-EC2-Price-Scraper).

![Example output of the script](https://github.com/jankais3r/AWS-EC2-Price-Scraper/blob/master/screen.png)

Now that we know which instance type we want to use, we need to find a vendor that offers that configuration. There are many vendors for each of the configurations, but for your convenience I’ve compiled a list of tested and verified ones here:
- g3s.xlarge running Windows (provided by Amazon): [link here](https://aws.amazon.com/marketplace/pp/B073WHLGMC)
- g3s.xlarge running Linux (provided by Canonical): [link here](https://aws.amazon.com/marketplace/pp/B07CQ33QKV)
- g4dn.xlarge running Windows (provided by Ingram Micro): [link here](https://aws.amazon.com/marketplace/pp/B07TS3S3ZH)
- g4dn.xlarge running Linux (provided by Ingram Micro): [link here](https://aws.amazon.com/marketplace/pp/B07YV3B14W)
- p3.2xlarge running Windows (provided by Ingram Micro): [link here](https://aws.amazon.com/marketplace/pp/B07TS3S3ZH)
- p3.2xlarge running Linux (provided by Canonical): [link here](https://aws.amazon.com/marketplace/pp/B07CQ33QKV)

The hourly rate for each instance type can also vary between different vendors, but those differences are usually much smaller than per-region variations within one vendor.


## What are the privacy implications of using cloud agents?

Here comes the disclaimer: This is not legal advice.

With that out of the way, let’s look at the technical side of things. Do the decrypted files end up (albeit temporarily) in Amazon’s cloud? The answer is, as usual, not that straightforward. There wasn’t a definitive answer out there, so I contacted Passware directly and this is what they said:

*“[…] files that might be fully transferred to the Agents are the following: ZIP, RAR, 7ZIP and PGP archives”*

This matches with the file types listed in Passware’s settings, where you can disable this behavior:

![Screenshot of option to disable file upload to agents](https://github.com/jankais3r/AWS-EC2-Price-Scraper/blob/master/Article_Images/5.png)

The sensible approach would be to disable this option when decrypting data belonging to EU citizens in non-EU-based datacenters, but as always it is good to check with your legal department. Alternatively, you can spin up a separate cloud agent based in the EU specifically for these file types.


## More technical considerations

There are two more EC2-specific technicalities that you should know about before starting with the cloud deployment.

### vCPU limits

Amazon maintains a limit of vCPUs for each account and region. To get that limit raised, you need to open a ticket with AWS support and specify which region and how many vCPUs you want to use. Keep in mind that the resolution of each ticket will take between half and two full working days. Also, if you ask for an unreasonable amount of cores right away, the request will most likely be denied. Start with something sensible, like 12 vCPUs allowing you to run 3 instances with 4 vCPUs each, and increase the limit as your needs grow over time.

![Screenshot of error related to low limit of vCPUs](https://github.com/jankais3r/AWS-EC2-Price-Scraper/blob/master/Article_Images/6.png)


### Static IP

If you plan to run the main Passware node on a corporate network, you will need to ask your network administrator to unblock UDP port 10555 from and to the IP address(es) of your cloud agent(s). The problem is that by default, every time you start an instance it will get assigned a new IP address, unless you [allocate an Elastic IP](https://console.aws.amazon.com/ec2/v2/home) to it. Amazon lets you reserve static IP addresses and assign them to your instances as you need. That is great, but you’ll be paying $0.005 per hour for every allocated IP address that is not currently associated to a running instance. Just factor that in your calculations.


## Key takeaways
- Currently, the best ratio of performance per money spent is g4dn.xlarge instance in the us-east-1, us-east-2, and us-west-2 regions. eu-north-1 is the currently the cheapest EU region. ap-south-1 is the cheapest Asia-Pacific region.
- ZIP, RAR, 7ZIP and PGP archives get uploaded to the cloud during the decryption process (this can be disabled in settings), so consider that when choosing the region of your cloud agents.
- You’ll need to [contact customer support](https://console.aws.amazon.com/support/home#case/create?issueType=service-limit-increase&limitType=service-code-ec2-instances&serviceLimitIncreaseType=ec2-instances&type=service_limit_increase) and ask them to raise your vCPU limit from 0 in every region you’ll want to spin up Agents in.
- Linux and Windows Agents provide the same level of performance, while Linux machines are generally cheaper.
- To match a performance of a single RTX 2080 Ti card you will need to spin up three g4dn.xlarge instances, which will cost you around $60 per day.
- Use the mentioned [Python script](https://github.com/jankais3r/AWS-EC2-Price-Scraper) to calculate the cheapest option at any moment


*This text has been originally published as a [LinkedIn article](https://www.linkedin.com/pulse/leveraging-power-cloud-distributed-password-cracking-jan-kaiser/) on March 13, 2020.*
